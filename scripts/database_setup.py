#!/usr/bin/env python3
"""
Database setup script for Test Automation Framework
Creates database tables and initial configuration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.database import db_manager, Base
from config.settings import settings
from core.logger import test_logger
import click

@click.group()
def cli():
    """Database setup and management commands."""
    pass

@cli.command()
@click.option('--url', help='Database URL (overrides .env)')
@click.option('--force', is_flag=True, help='Force recreate tables')
def init(url, force):
    """Initialize database tables."""
    try:
        if url:
            # Temporarily override database URL
            original_url = settings.database.url
            settings.database.url = url
            # Recreate db_manager with new URL
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            db_manager.engine = create_engine(url)
            db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        
        click.echo("🔧 Initializing database...")
        
        if force:
            click.echo("⚠️  Dropping existing tables...")
            Base.metadata.drop_all(bind=db_manager.engine)
        
        # Create tables
        db_manager.create_tables()
        click.echo("✅ Database tables created successfully!")
        
        # Test connection
        with db_manager.get_session() as session:
            result = session.execute("SELECT 1").fetchone()
            if result:
                click.echo("✅ Database connection test passed!")
            
    except Exception as e:
        click.echo(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

@cli.command()
def check():
    """Check database connection and tables."""
    try:
        click.echo("🔍 Checking database connection...")
        
        # Test connection
        with db_manager.get_session() as session:
            result = session.execute("SELECT 1").fetchone()
            if result:
                click.echo("✅ Database connection successful!")
            
        # Check tables
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['test_runs', 'test_results']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            click.echo(f"⚠️  Missing tables: {missing_tables}")
            click.echo("Run 'python scripts/database_setup.py init' to create them")
        else:
            click.echo("✅ All required tables exist!")
            
        click.echo(f"📊 Found tables: {tables}")
        
    except Exception as e:
        click.echo(f"❌ Database check failed: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--days', default=30, help='Number of days to keep')
def cleanup(days):
    """Clean up old test results."""
    try:
        from datetime import datetime, timedelta
        from config.database import TestRun, TestResult
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db_manager.get_session() as session:
            # Count records to be deleted
            old_runs = session.query(TestRun).filter(TestRun.start_time < cutoff_date).count()
            old_results = session.query(TestResult).filter(TestResult.start_time < cutoff_date).count()
            
            if old_runs == 0 and old_results == 0:
                click.echo("✅ No old records to clean up!")
                return
            
            click.echo(f"🗑️  Found {old_runs} test runs and {old_results} test results older than {days} days")
            
            if click.confirm("Do you want to delete these records?"):
                # Delete old records
                session.query(TestResult).filter(TestResult.start_time < cutoff_date).delete()
                session.query(TestRun).filter(TestRun.start_time < cutoff_date).delete()
                session.commit()
                
                click.echo("✅ Old records cleaned up successfully!")
            else:
                click.echo("❌ Cleanup cancelled")
                
    except Exception as e:
        click.echo(f"❌ Cleanup failed: {str(e)}")
        sys.exit(1)

@cli.command()
def stats():
    """Show database statistics."""
    try:
        from config.database import TestRun, TestResult
        from sqlalchemy import func
        
        with db_manager.get_session() as session:
            # Test runs stats
            total_runs = session.query(TestRun).count()
            completed_runs = session.query(TestRun).filter(TestRun.status == 'completed').count()
            failed_runs = session.query(TestRun).filter(TestRun.status.in_(['failed', 'error'])).count()
            
            # Test results stats
            total_tests = session.query(TestResult).count()
            passed_tests = session.query(TestResult).filter(TestResult.status == 'passed').count()
            failed_tests = session.query(TestResult).filter(TestResult.status.in_(['failed', 'error'])).count()
            
            # Recent activity
            recent_runs = session.query(TestRun).filter(
                TestRun.start_time >= func.now() - func.interval('7 days')
            ).count()
            
            click.echo("📊 Database Statistics:")
            click.echo(f"   Test Runs: {total_runs} total, {completed_runs} completed, {failed_runs} failed")
            click.echo(f"   Test Results: {total_tests} total, {passed_tests} passed, {failed_tests} failed")
            click.echo(f"   Recent Activity: {recent_runs} runs in last 7 days")
            
            if total_tests > 0:
                pass_rate = (passed_tests / total_tests) * 100
                click.echo(f"   Overall Pass Rate: {pass_rate:.1f}%")
                
    except Exception as e:
        click.echo(f"❌ Stats query failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    cli()