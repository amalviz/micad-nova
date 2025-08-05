"""
Database configuration and models for test results storage.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
from config.settings import settings

Base = declarative_base()

class TestRun(Base):
    """Model for storing test run information."""
    __tablename__ = "test_runs"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(50), unique=True, nullable=False)
    platform = Column(String(20), nullable=False)  # web, mobile
    application = Column(String(50), nullable=True)
    environment = Column(String(20), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # running, passed, failed, error
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    test_metadata = Column(JSON, nullable=True)

class TestResult(Base):
    """Model for storing individual test results."""
    __tablename__ = "test_results"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(50), nullable=False)
    test_name = Column(String(200), nullable=False)
    test_class = Column(String(200), nullable=True)
    test_module = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False)  # passed, failed, skipped, error
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # in milliseconds
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    test_metadata = Column(JSON, nullable=True)

class DatabaseManager:
    """Database manager for handling test results storage."""
    
    def __init__(self):
        try:
            self.engine = create_engine(
                settings.database.url,
                pool_size=settings.database.pool_size,
                echo=settings.database.echo,
                # PostgreSQL specific settings
                pool_pre_ping=True,
                pool_recycle=300
            )
        except Exception as e:
            # Fallback to SQLite if PostgreSQL is not available
            fallback_url = "sqlite:///test_results.db"
            self.engine = create_engine(fallback_url, echo=settings.database.echo)
            print(f"PostgreSQL connection failed, using SQLite fallback: {e}")
            
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def create_test_run(self, run_id: str, platform: str, application: Optional[str] = None, 
                       environment: str = "test", metadata: Optional[Dict[str, Any]] = None) -> TestRun:
        """Create a new test run record."""
        with self.get_session() as session:
            test_run = TestRun(
                run_id=run_id,
                platform=platform,
                application=application,
                environment=environment,
                status="running",
                metadata=metadata
            )
            session.add(test_run)
            session.commit()
            session.refresh(test_run)
            return test_run
    
    def update_test_run(self, run_id: str, **kwargs):
        """Update test run record."""
        with self.get_session() as session:
            test_run = session.query(TestRun).filter(TestRun.run_id == run_id).first()
            if test_run:
                for key, value in kwargs.items():
                    setattr(test_run, key, value)
                session.commit()
    
    def create_test_result(self, run_id: str, test_name: str, status: str, **kwargs) -> TestResult:
        """Create a new test result record."""
        with self.get_session() as session:
            test_result = TestResult(
                run_id=run_id,
                test_name=test_name,
                status=status,
                **kwargs
            )
            session.add(test_result)
            session.commit()
            session.refresh(test_result)
            return test_result
    
    def get_test_run(self, run_id: str) -> Optional[TestRun]:
        """Get test run by ID."""
        with self.get_session() as session:
            return session.query(TestRun).filter(TestRun.run_id == run_id).first()
    
    def get_test_results(self, run_id: str) -> list:
        """Get all test results for a run."""
        with self.get_session() as session:
            return session.query(TestResult).filter(TestResult.run_id == run_id).all()
    
    def get_failed_tests(self, run_id: str) -> list:
        """Get failed tests for AI analysis."""
        with self.get_session() as session:
            return session.query(TestResult).filter(
                TestResult.run_id == run_id,
                TestResult.status.in_(["failed", "error"])
            ).all()

# Global database manager instance
db_manager = DatabaseManager()