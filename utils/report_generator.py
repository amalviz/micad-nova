"""
Report generation utilities for test results.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
from core.logger import test_logger
from config.settings import settings
from config.database import db_manager

class HTMLReportGenerator:
    """Generate HTML reports for test results."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self._create_default_template()
    
    def _create_default_template(self):
        """Create default HTML template if it doesn't exist."""
        template_path = self.template_dir / "test_report.html"
        
        if not template_path.exists():
            template_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Automation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .summary-card.passed { border-left-color: #28a745; }
        .summary-card.failed { border-left-color: #dc3545; }
        .summary-card.skipped { border-left-color: #ffc107; }
        .test-results { margin-top: 30px; }
        .test-item { background: white; margin-bottom: 15px; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
        .test-item.passed { border-left: 4px solid #28a745; }
        .test-item.failed { border-left: 4px solid #dc3545; }
        .test-item.skipped { border-left: 4px solid #ffc107; }
        .test-header { display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }
        .test-name { font-weight: bold; font-size: 1.1em; }
        .test-status { padding: 4px 12px; border-radius: 20px; color: white; font-size: 0.9em; }
        .status-passed { background-color: #28a745; }
        .status-failed { background-color: #dc3545; }
        .status-skipped { background-color: #ffc107; color: #000; }
        .test-details { margin-top: 15px; }
        .error-message { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin-top: 10px; font-family: monospace; }
        .ai-analysis { background: #e7f3ff; padding: 15px; border-radius: 4px; margin-top: 10px; border-left: 4px solid #007bff; }
        .suggestions { margin-top: 10px; }
        .suggestions ul { margin: 0; padding-left: 20px; }
        .chart-container { margin: 30px 0; text-align: center; }
        .metadata { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Automation Report</h1>
            <p>Generated on {{ report_date }} | Run ID: {{ run_id }}</p>
            <p>Platform: {{ platform }} | Duration: {{ duration }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <h2>{{ total_tests }}</h2>
            </div>
            <div class="summary-card passed">
                <h3>Passed</h3>
                <h2>{{ passed_tests }}</h2>
                <p>{{ pass_rate }}%</p>
            </div>
            <div class="summary-card failed">
                <h3>Failed</h3>
                <h2>{{ failed_tests }}</h2>
                <p>{{ fail_rate }}%</p>
            </div>
            <div class="summary-card skipped">
                <h3>Skipped</h3>
                <h2>{{ skipped_tests }}</h2>
                <p>{{ skip_rate }}%</p>
            </div>
        </div>
        
        {% if ai_analysis %}
        <div class="ai-analysis">
            <h3>🤖 AI Analysis Summary</h3>
            <p><strong>Most Common Failure:</strong> {{ ai_analysis.most_common_category }}</p>
            <div class="suggestions">
                <strong>Recommendations:</strong>
                <ul>
                    {% for recommendation in ai_analysis.recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}
        
        <div class="test-results">
            <h2>Test Results</h2>
            {% for test in test_results %}
            <div class="test-item {{ test.status }}">
                <div class="test-header">
                    <div class="test-name">{{ test.test_name }}</div>
                    <div class="test-status status-{{ test.status }}">{{ test.status.upper() }}</div>
                </div>
                
                <div class="test-details">
                    <p><strong>Class:</strong> {{ test.test_class or 'N/A' }}</p>
                    <p><strong>Duration:</strong> {{ test.duration }}ms</p>
                    
                    {% if test.error_message %}
                    <div class="error-message">
                        <strong>Error:</strong><br>
                        {{ test.error_message }}
                    </div>
                    {% endif %}
                    
                    {% if test.ai_analysis %}
                    <div class="ai-analysis">
                        <strong>🤖 AI Analysis:</strong>
                        <p><strong>Category:</strong> {{ test.ai_analysis.category }} ({{ test.ai_analysis.confidence }}% confidence)</p>
                        <p><strong>Root Cause:</strong> {{ test.ai_analysis.root_cause }}</p>
                        <div class="suggestions">
                            <strong>Suggestions:</strong>
                            <ul>
                                {% for suggestion in test.ai_analysis.suggestions %}
                                <li>{{ suggestion }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if test.screenshot_path %}
                    <div class="metadata">
                        <strong>Screenshot:</strong> <a href="{{ test.screenshot_path }}" target="_blank">View Screenshot</a>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
            '''
            
            with open(template_path, 'w') as f:
                f.write(template_content.strip())
    
    def generate_report(self, run_id: str, output_path: Optional[str] = None) -> str:
        """Generate HTML report for a test run."""
        try:
            # Get test run data
            test_run = db_manager.get_test_run(run_id)
            test_results = db_manager.get_test_results(run_id)
            
            if not test_run:
                raise ValueError(f"Test run not found: {run_id}")
            
            # Calculate summary statistics
            total_tests = len(test_results)
            passed_tests = len([t for t in test_results if t.status == 'passed'])
            failed_tests = len([t for t in test_results if t.status == 'failed'])
            skipped_tests = len([t for t in test_results if t.status == 'skipped'])
            
            pass_rate = round((passed_tests / total_tests * 100), 1) if total_tests > 0 else 0
            fail_rate = round((failed_tests / total_tests * 100), 1) if total_tests > 0 else 0
            skip_rate = round((skipped_tests / total_tests * 100), 1) if total_tests > 0 else 0
            
            # Calculate duration
            duration = "N/A"
            if test_run.start_time and test_run.end_time:
                duration_seconds = (test_run.end_time - test_run.start_time).total_seconds()
                duration = f"{duration_seconds:.1f}s"
            
            # Prepare AI analysis if available
            ai_analysis = None
            if settings.ai.enabled and failed_tests > 0:
                from utils.ai_analyzer import ai_analyzer
                if ai_analyzer:
                    failed_test_data = [
                        {
                            'test_name': t.test_name,
                            'status': t.status,
                            'error_message': t.error_message,
                            'stack_trace': t.stack_trace
                        }
                        for t in test_results if t.status in ['failed', 'error']
                    ]
                    ai_report = ai_analyzer.generate_report(failed_test_data)
                    ai_analysis = ai_report.get('summary', {})
            
            # Prepare template data
            template_data = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'run_id': run_id,
                'platform': test_run.platform,
                'duration': duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'skipped_tests': skipped_tests,
                'pass_rate': pass_rate,
                'fail_rate': fail_rate,
                'skip_rate': skip_rate,
                'test_results': [
                    {
                        'test_name': t.test_name,
                        'test_class': t.test_class,
                        'status': t.status,
                        'duration': t.duration or 0,
                        'error_message': t.error_message,
                        'screenshot_path': t.screenshot_path,
                        'ai_analysis': json.loads(t.ai_analysis) if t.ai_analysis else None
                    }
                    for t in test_results
                ],
                'ai_analysis': ai_analysis
            }
            
            # Load and render template
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template('test_report.html')
            html_content = template.render(**template_data)
            
            # Save report
            if not output_path:
                reports_dir = settings.get_reports_dir()
                output_path = reports_dir / f"test_report_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            test_logger.info(f"HTML report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            test_logger.error(f"Failed to generate HTML report: {str(e)}")
            raise

class JSONReportGenerator:
    """Generate JSON reports for test results."""
    
    def generate_report(self, run_id: str, output_path: Optional[str] = None) -> str:
        """Generate JSON report for a test run."""
        try:
            # Get test run data
            test_run = db_manager.get_test_run(run_id)
            test_results = db_manager.get_test_results(run_id)
            
            if not test_run:
                raise ValueError(f"Test run not found: {run_id}")
            
            # Prepare report data
            report_data = {
                'run_info': {
                    'run_id': test_run.run_id,
                    'platform': test_run.platform,
                    'application': test_run.application,
                    'environment': test_run.environment,
                    'start_time': test_run.start_time.isoformat() if test_run.start_time else None,
                    'end_time': test_run.end_time.isoformat() if test_run.end_time else None,
                    'status': test_run.status,
                    'metadata': test_run.metadata
                },
                'summary': {
                    'total_tests': test_run.total_tests,
                    'passed_tests': test_run.passed_tests,
                    'failed_tests': test_run.failed_tests,
                    'skipped_tests': test_run.skipped_tests
                },
                'test_results': [
                    {
                        'test_name': t.test_name,
                        'test_class': t.test_class,
                        'test_module': t.test_module,
                        'status': t.status,
                        'start_time': t.start_time.isoformat() if t.start_time else None,
                        'end_time': t.end_time.isoformat() if t.end_time else None,
                        'duration': t.duration,
                        'error_message': t.error_message,
                        'stack_trace': t.stack_trace,
                        'screenshot_path': t.screenshot_path,
                        'video_path': t.video_path,
                        'ai_analysis': json.loads(t.ai_analysis) if t.ai_analysis else None,
                        'metadata': t.metadata
                    }
                    for t in test_results
                ]
            }
            
            # Save report
            if not output_path:
                reports_dir = settings.get_reports_dir()
                output_path = reports_dir / f"test_report_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            test_logger.info(f"JSON report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            test_logger.error(f"Failed to generate JSON report: {str(e)}")
            raise

class ReportManager:
    """Manage report generation for different formats."""
    
    def __init__(self):
        self.generators = {
            'html': HTMLReportGenerator(),
            'json': JSONReportGenerator()
        }
    
    def generate_reports(self, run_id: str, formats: List[str] = None) -> Dict[str, str]:
        """Generate reports in specified formats."""
        if not formats:
            formats = settings.reporting.formats
        
        report_paths = {}
        
        for format_name in formats:
            if format_name in self.generators:
                try:
                    path = self.generators[format_name].generate_report(run_id)
                    report_paths[format_name] = path
                except Exception as e:
                    test_logger.error(f"Failed to generate {format_name} report: {str(e)}")
            else:
                test_logger.warning(f"Unsupported report format: {format_name}")
        
        return report_paths

# Global report manager instance
report_manager = ReportManager()