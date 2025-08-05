"""
Command-line interface for the test automation framework.
"""
import click
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from core.logger import test_logger
from config.settings import settings
from config.database import db_manager
from core.test_tracker import tracker_manager

# Try to import optional dependencies
try:
    from utils.report_generator import report_manager
    REPORTING_AVAILABLE = True
except ImportError:
    REPORTING_AVAILABLE = False
    class report_manager:
        @staticmethod
        def generate_reports(*args, **kwargs): return {}

try:
    from utils.ai_analyzer import ai_analyzer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    ai_analyzer = None

try:
    import subprocess
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

@click.group()
@click.version_option(version="1.0.0", prog_name="Test Automation Framework")
def cli():
    """Test Automation Framework CLI - Run web and mobile tests with AI-powered analysis."""
    pass

@cli.command()
@click.option('--platform', type=click.Choice(['web', 'mobile']), required=True,
              help='Platform to test (web or mobile)')
@click.option('--app', help='Application name to test')
@click.option('--environment', default='test', help='Test environment')
@click.option('--browser', help='Browser for web tests (chromium, firefox, webkit)')
@click.option('--headless', is_flag=True, help='Run browser in headless mode')
@click.option('--device', help='Device name for mobile tests')
@click.option('--parallel', type=int, help='Number of parallel workers')
@click.option('--test-pattern', help='Test file pattern to run')
@click.option('--ai-analysis', is_flag=True, help='Enable AI-powered failure analysis')
@click.option('--report-format', multiple=True, help='Report formats (html, json, allure)')
@click.option('--output-dir', help='Output directory for reports')
@click.option('--retry', type=int, default=0, help='Number of retries for failed tests')
@click.option('--timeout', type=int, help='Test timeout in seconds')
@click.option('--verbose', is_flag=True, help='Verbose logging')
def run(platform: str, app: Optional[str], environment: str, browser: Optional[str],
        headless: bool, device: Optional[str], parallel: Optional[int],
        test_pattern: Optional[str], ai_analysis: bool, report_format: tuple,
        output_dir: Optional[str], retry: int, timeout: Optional[int], verbose: bool):
    """Run tests on specified platform."""
    
    if not SUBPROCESS_AVAILABLE:
        click.echo("Error: subprocess module not available in this environment")
        click.echo("Tests cannot be executed directly. Please run tests manually using:")
        click.echo(f"python -m pytest tests/{platform}/")
        return
    
    # Generate run ID
    run_id = str(uuid.uuid4())
    
    # Override settings if provided
    if browser:
        settings.web.browser = browser
    if headless:
        settings.web.headless = headless
    if device:
        settings.mobile.device_name = device
    if parallel:
        settings.general.parallel_workers = parallel
    if retry:
        settings.general.retry_failed_tests = retry
    if timeout:
        settings.general.test_timeout = timeout
    if ai_analysis:
        settings.ai.enabled = True
    if report_format:
        settings.reporting.formats = list(report_format)
    if output_dir:
        settings.reporting.output_dir = output_dir
    if verbose:
        settings.logging.level = "DEBUG"
    
    test_logger.info(f"Starting test run: {run_id}")
    test_logger.info(f"Platform: {platform}, Environment: {environment}")
    
    # Create test tracker for Supabase
    app_type = 'Web' if platform == 'web' else 'Mobile'
    test_tracker = tracker_manager.create_tracker(run_id, app_type, app)
    
    # Create in database
    try:
        db_manager.create_test_run(
            run_id=run_id,
            platform=platform,
            application=app,
            environment=environment,
            test_metadata={
                'browser': browser,
                'device': device,
                'parallel_workers': settings.general.parallel_workers,
                'test_metadata': getattr(t, 'test_metadata', t.get('metadata', {}))
            }
        )
    except Exception as e:
        test_logger.warning(f"Database not available: {str(e)}")
    
    try:
        # Run tests
        results = asyncio.run(_run_tests(run_id, platform, app, test_pattern))
        
        # Update test tracker with results
        test_tracker.update_run_summary(
            total_tests=results['total'],
            passed_tests=results['passed'],
            failed_tests=results['failed'],
            skipped_tests=results['skipped'],
            status='completed'
        )
        
        # Update legacy database if available
        end_time = datetime.utcnow()
        try:
            db_manager.update_test_run(
                run_id=run_id,
                end_time=end_time,
                status='completed',
                total_tests=results['total'],
                passed_tests=results['passed'],
                failed_tests=results['failed'],
                skipped_tests=results['skipped']
            )
        except Exception as e:
            test_logger.warning(f"Database update failed: {str(e)}")
        
        # Generate reports
        if REPORTING_AVAILABLE:
            test_logger.info("Generating reports...")
            report_paths = report_manager.generate_reports(run_id)
        else:
            test_logger.info("Report generation not available in this environment")
            report_paths = {}
        
        # Display results
        _display_results(results, report_paths)
        
        # Perform AI analysis if enabled and there are failures
        if settings.ai.enabled and results['failed'] > 0 and AI_AVAILABLE and ai_analyzer:
            test_logger.info("Performing AI analysis...")
            failed_tests = db_manager.get_failed_tests(run_id)
            if failed_tests:
                ai_report = ai_analyzer.generate_report([
                    {
                        'test_name': t.test_name,
                        'error_message': t.error_message,
                        'stack_trace': t.stack_trace
                    }
                    for t in failed_tests
                ])
                _display_ai_analysis(ai_report)
        elif settings.ai.enabled and not AI_AVAILABLE:
            test_logger.info("AI analysis not available in this environment")
        
        # Exit with error code if tests failed
        exit_code = 1 if results['failed'] > 0 else 0
        exit(exit_code)
        
    except Exception as e:
        test_logger.error(f"Test run failed: {str(e)}")
        
        # Update both tracking systems
        test_tracker.update_run_summary(0, 0, 0, 0, status='failed')
        try:
            db_manager.update_test_run(run_id=run_id, status='error', end_time=datetime.utcnow())
        except:
            pass
        
        exit(1)

async def _run_tests(run_id: str, platform: str, app: Optional[str], 
                    test_pattern: Optional[str]) -> dict:
    """Run the actual tests."""
    
    # Build pytest command
    pytest_args = []
    
    # Add test directory based on platform
    if platform == 'web':
        test_dir = 'tests/web'
    elif platform == 'mobile':
        test_dir = 'tests/mobile'
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    pytest_args.append(test_dir)
    
    # Add app-specific tests if specified
    if app:
        app_test_dir = Path(test_dir) / app
        if app_test_dir.exists():
            pytest_args = [str(app_test_dir)]
    
    # Add test pattern if specified
    if test_pattern:
        pytest_args.extend(['-k', test_pattern])
    
    # Add parallel execution (only if pytest-xdist is available)
    if settings.general.parallel_workers > 1:
        try:
            import pytest_xdist
            pytest_args.extend(['-n', str(settings.general.parallel_workers)])
        except ImportError:
            test_logger.warning("pytest-xdist not available, running tests sequentially")
    
    # Add retry logic (only if pytest-rerunfailures is available)
    if settings.general.retry_failed_tests > 0:
        try:
            import pytest_rerunfailures
            pytest_args.extend(['--tb=short', f'--reruns={settings.general.retry_failed_tests}'])
        except ImportError:
            test_logger.warning("pytest-rerunfailures not available, no retry logic")
    
    # Add HTML report (only if pytest-html is available)
    try:
        import pytest_html
        html_report_path = settings.get_reports_dir() / f'pytest_report_{run_id}.html'
        pytest_args.extend(['--html', str(html_report_path), '--self-contained-html'])
    except ImportError:
        test_logger.warning("pytest-html not available, no HTML report will be generated")
    
    # Set run ID for tests
    import os
    os.environ['TEST_RUN_ID'] = run_id
    os.environ['TEST_APPLICATION'] = app or 'unknown'
    
    # Import and run pytest
    import pytest
    
    test_logger.info(f"Running pytest with args: {' '.join(pytest_args)}")
    exit_code = pytest.main(pytest_args)
    
    # Get results from database
    try:
        test_results = db_manager.get_test_results(run_id)
        
        results = {
            'total': len(test_results),
            'passed': len([t for t in test_results if t.status == 'passed']),
            'failed': len([t for t in test_results if t.status in ['failed', 'error']]),
            'skipped': len([t for t in test_results if t.status == 'skipped']),
            'exit_code': exit_code
        }
    except Exception as e:
        test_logger.warning(f"Failed to get test results from database: {str(e)}")
        # Fallback to basic results based on exit code
        results = {
            'total': 0,
            'passed': 0 if exit_code != 0 else 1,
            'failed': 1 if exit_code != 0 else 0,
            'skipped': 0,
            'exit_code': exit_code
        }
    
    return results

def _display_results(results: dict, report_paths: dict):
    """Display test results summary."""
    click.echo("\n" + "="*60)
    click.echo("TEST RESULTS SUMMARY")
    click.echo("="*60)
    
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    skipped = results['skipped']
    
    click.echo(f"Total Tests: {total}")
    click.echo(f"Passed: {click.style(str(passed), fg='green')} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0")
    click.echo(f"Failed: {click.style(str(failed), fg='red')} ({failed/total*100:.1f}%)" if total > 0 else "Failed: 0")
    click.echo(f"Skipped: {click.style(str(skipped), fg='yellow')} ({skipped/total*100:.1f}%)" if total > 0 else "Skipped: 0")
    
    if report_paths:
        click.echo("\nREPORTS GENERATED:")
        for format_name, path in report_paths.items():
            click.echo(f"  {format_name.upper()}: {path}")
    
    click.echo("="*60)

def _display_ai_analysis(ai_report: dict):
    """Display AI analysis results."""
    if 'summary' not in ai_report:
        return
    
    summary = ai_report['summary']
    
    click.echo("\n" + "="*60)
    click.echo("🤖 AI FAILURE ANALYSIS")
    click.echo("="*60)
    
    click.echo(f"Total Failures Analyzed: {summary.get('total_failures', 0)}")
    
    if 'most_common_category' in summary:
        click.echo(f"Most Common Issue: {click.style(summary['most_common_category'], fg='red')}")
    
    if 'categories' in summary:
        click.echo("\nFailure Categories:")
        for category, count in summary['categories'].items():
            click.echo(f"  {category}: {count}")
    
    if 'recommendations' in ai_report:
        click.echo(f"\n{click.style('Recommendations:', fg='blue', bold=True)}")
        for i, rec in enumerate(ai_report['recommendations'], 1):
            click.echo(f"  {i}. {rec}")
    
    click.echo("="*60)

@cli.command()
@click.option('--run-id', required=True, help='Test run ID to generate report for')
@click.option('--format', 'formats', multiple=True, 
              type=click.Choice(['html', 'json']), 
              help='Report formats to generate')
@click.option('--output-dir', help='Output directory for reports')
def report(run_id: str, formats: tuple, output_dir: Optional[str]):
    """Generate reports for a specific test run."""
    
    if not REPORTING_AVAILABLE:
        click.echo("Report generation not available in this environment")
        return
    
    if output_dir:
        settings.reporting.output_dir = output_dir
    
    if formats:
        report_formats = list(formats)
    else:
        report_formats = settings.reporting.formats
    
    try:
        test_logger.info(f"Generating reports for run: {run_id}")
        report_paths = report_manager.generate_reports(run_id, report_formats)
        
        click.echo("Reports generated:")
        for format_name, path in report_paths.items():
            click.echo(f"  {format_name.upper()}: {path}")
            
    except Exception as e:
        test_logger.error(f"Failed to generate reports: {str(e)}")
        exit(1)

@cli.command()
@click.option('--run-id', help='Analyze specific test run')
@click.option('--failed-only', is_flag=True, help='Analyze only failed tests')
def analyze(run_id: Optional[str], failed_only: bool):
    """Perform AI analysis on test results."""
    
    if not settings.ai.enabled:
        click.echo("AI analysis is not enabled. Set ENABLE_AI_ANALYSIS=true in your environment.")
        exit(1)
    
    if not AI_AVAILABLE or not ai_analyzer:
        click.echo("AI analyzer not available in this environment.")
        exit(1)
    
    try:
        if run_id:
            # Analyze specific run
            if failed_only:
                test_results = db_manager.get_failed_tests(run_id)
            else:
                test_results = db_manager.get_test_results(run_id)
            
            test_data = [
                {
                    'test_name': t.test_name,
                    'status': t.status,
                    'error_message': t.error_message,
                    'stack_trace': t.stack_trace
                }
                for t in test_results
            ]
            
            ai_report = ai_analyzer.generate_report(test_data)
            _display_ai_analysis(ai_report)
        else:
            click.echo("Please specify --run-id to analyze")
            exit(1)
            
    except Exception as e:
        test_logger.error(f"Analysis failed: {str(e)}")
        exit(1)

@cli.command()
@click.option('--days', default=30, help='Number of days to look back')
@click.option('--platform', type=click.Choice(['web', 'mobile']), help='Filter by platform')
def history(days: int, platform: Optional[str]):
    """Show test run history."""
    
    try:
        from datetime import timedelta
        from sqlalchemy import and_
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db_manager.get_session() as session:
            from config.database import TestRun
            
            query = session.query(TestRun).filter(TestRun.start_time >= cutoff_date)
            
            if platform:
                query = query.filter(TestRun.platform == platform)
            
            test_runs = query.order_by(TestRun.start_time.desc()).limit(20).all()
        
        if not test_runs:
            click.echo("No test runs found in the specified period.")
            return
        
        click.echo(f"\nTEST RUN HISTORY (Last {days} days)")
        click.echo("="*80)
        click.echo(f"{'Run ID':<36} {'Platform':<8} {'Status':<10} {'Tests':<6} {'Date':<19}")
        click.echo("-"*80)
        
        for run in test_runs:
            run_id_short = run.run_id[:8] + "..."
            date_str = run.start_time.strftime('%Y-%m-%d %H:%M:%S') if run.start_time else 'Unknown'
            
            status_color = 'green' if run.status == 'completed' else 'red'
            status = click.style(run.status, fg=status_color)
            
            click.echo(f"{run_id_short:<36} {run.platform:<8} {status:<10} {run.total_tests:<6} {date_str}")
        
    except Exception as e:
        test_logger.error(f"Failed to get history: {str(e)}")
        exit(1)

@cli.command()
def list_tests():
    """List all available tests."""
    if not Path("tests").exists():
        click.echo("No tests directory found")
        return
        
    click.echo("Available tests:")
    
    test_dirs = ["tests/web", "tests/mobile"]
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            click.echo(f"\n{test_dir}:")
            for test_file in Path(test_dir).rglob("test_*.py"):
                click.echo(f"  {test_file.relative_to(test_dir)}")

@cli.command()
def setup_environment():
    """Setup test environment and dependencies."""
    click.echo("Setting up test environment (limited in WebContainer)...")
    
    try:
        # Create necessary directories  
        directories = [
            "tests/web",
            "tests/mobile",
            "reports",
            "logs",
            "screenshots"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        click.echo("✓ Directory structure created")
        
        # Note about limitations
        click.echo("Note: Full browser and mobile driver setup requires additional configuration")
        click.echo("Environment basic setup completed!")
        
    except Exception as e:
        click.echo(f"Error setting up environment: {e}")

    # Import os at module level to avoid issues
    import os

def main():
    """Main entry point for CLI."""
    cli()

if __name__ == '__main__':
    main()