"""
Test execution tracking and reporting to Supabase.
"""
import uuid
import time
from typing import Optional, Dict, Any
from datetime import datetime
from core.logger import test_logger
from config.supabase_client import supabase_manager

class TestTracker:
    """Track test executions and sync with Supabase."""
    
    def __init__(self, run_id: str, app_type: str, application: Optional[str] = None):
        self.run_id = run_id
        self.app_type = app_type
        self.application = application
        self.current_execution_id = None
        self.test_start_time = None
        
        # Create test run in database
        self._create_test_run()
    
    def _create_test_run(self):
        """Create test run record in Supabase."""
        try:
            supabase_manager.create_test_run(
                run_id=self.run_id,
                app_type=self.app_type,
                application=self.application,
                environment="test",
                test_metadata={
                    'framework_version': '1.0.0',
                    'created_by': 'test_automation_framework'
                }
            )
            test_logger.info(f"Test run tracking started: {self.run_id}")
        except Exception as e:
            test_logger.error(f"Failed to create test run tracking: {str(e)}")
    
    def start_test(self, testcase_name: str, testcase_description: Optional[str] = None, 
                   test_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start tracking a test execution."""
        self.test_start_time = time.time()
        
        try:
            result = supabase_manager.create_test_execution(
                run_id=self.run_id,
                app_type=self.app_type,
                application=self.application,
                testcase_name=testcase_name,
                testcase_description=testcase_description,
                test_status='running',
                test_metadata=test_metadata
            )
            
            if result:
                self.current_execution_id = result['id']
                test_logger.test_start(testcase_name)
                return self.current_execution_id
            else:
                test_logger.error(f"Failed to start test tracking: {testcase_name}")
                return str(uuid.uuid4())  # Fallback ID
                
        except Exception as e:
            test_logger.error(f"Failed to start test tracking: {str(e)}")
            return str(uuid.uuid4())  # Fallback ID
    
    def end_test(self, test_status: str, error_message: Optional[str] = None, 
                stack_trace: Optional[str] = None, screenshot_path: Optional[str] = None,
                video_path: Optional[str] = None, test_metadata: Optional[Dict[str, Any]] = None):
        """End tracking a test execution."""
        if not self.current_execution_id or not self.test_start_time:
            test_logger.warning("No active test to end")
            return
        
        # Calculate duration
        test_duration = int((time.time() - self.test_start_time) * 1000)  # Convert to milliseconds
        
        try:
            supabase_manager.update_test_execution(
                execution_id=self.current_execution_id,
                test_status=test_status,
                test_duration=test_duration,
                error_message=error_message,
                stack_trace=stack_trace,
                screenshot_path=screenshot_path,
                video_path=video_path,
                test_metadata=test_metadata
            )
            
            # Log test result
            if test_status == 'passed':
                test_logger.test_pass(f"Test {self.current_execution_id}", test_duration / 1000)
            elif test_status in ['failed', 'error']:
                test_logger.test_fail(f"Test {self.current_execution_id}", error_message, test_duration / 1000)
            elif test_status == 'skipped':
                test_logger.test_skip(f"Test {self.current_execution_id}", error_message)
            
        except Exception as e:
            test_logger.error(f"Failed to end test tracking: {str(e)}")
        finally:
            self.current_execution_id = None
            self.test_start_time = None
    
    def update_run_summary(self, total_tests: int, passed_tests: int, failed_tests: int, 
                          skipped_tests: int, status: str = 'completed'):
        """Update test run summary."""
        try:
            supabase_manager.update_test_run(
                run_id=self.run_id,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                status=status,
                end_time=datetime.utcnow().isoformat()
            )
            test_logger.info(f"Test run summary updated: {self.run_id}")
        except Exception as e:
            test_logger.error(f"Failed to update run summary: {str(e)}")
    
    def add_screenshot(self, screenshot_path: str):
        """Add screenshot to current test execution."""
        if not self.current_execution_id:
            test_logger.warning("No active test to add screenshot to")
            return
        
        try:
            supabase_manager.update_test_execution(
                execution_id=self.current_execution_id,
                screenshot_path=screenshot_path
            )
            test_logger.screenshot_taken(screenshot_path)
        except Exception as e:
            test_logger.error(f"Failed to add screenshot: {str(e)}")
    
    def add_video(self, video_path: str):
        """Add video recording to current test execution."""
        if not self.current_execution_id:
            test_logger.warning("No active test to add video to")
            return
        
        try:
            supabase_manager.update_test_execution(
                execution_id=self.current_execution_id,
                video_path=video_path
            )
            test_logger.video_recorded(video_path)
        except Exception as e:
            test_logger.error(f"Failed to add video: {str(e)}")
    
    def get_run_statistics(self) -> Dict[str, Any]:
        """Get statistics for current test run."""
        try:
            executions = supabase_manager.get_test_executions(self.run_id)
            
            if not executions:
                return {}
            
            total = len(executions)
            passed = len([e for e in executions if e['test_status'] == 'passed'])
            failed = len([e for e in executions if e['test_status'] == 'failed'])
            error = len([e for e in executions if e['test_status'] == 'error'])
            skipped = len([e for e in executions if e['test_status'] == 'skipped'])
            
            return {
                'run_id': self.run_id,
                'total_tests': total,
                'passed_tests': passed,
                'failed_tests': failed + error,
                'skipped_tests': skipped,
                'pass_rate': round((passed / total * 100), 2) if total > 0 else 0,
                'executions': executions
            }
            
        except Exception as e:
            test_logger.error(f"Failed to get run statistics: {str(e)}")
            return {}

class TestTrackerManager:
    """Manage test trackers for different test runs."""
    
    def __init__(self):
        self.trackers: Dict[str, TestTracker] = {}
    
    def create_tracker(self, run_id: str, app_type: str, application: Optional[str] = None) -> TestTracker:
        """Create a new test tracker."""
        tracker = TestTracker(run_id, app_type, application)
        self.trackers[run_id] = tracker
        return tracker
    
    def get_tracker(self, run_id: str) -> Optional[TestTracker]:
        """Get existing test tracker."""
        return self.trackers.get(run_id)
    
    def remove_tracker(self, run_id: str):
        """Remove test tracker."""
        if run_id in self.trackers:
            del self.trackers[run_id]

# Global tracker manager
tracker_manager = TestTrackerManager()