"""
Supabase client configuration and utilities.
"""
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from core.logger import test_logger

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    test_logger.warning("Supabase client not available. Install supabase-py to enable database features.")

class SupabaseManager:
    """Manager for Supabase database operations."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client."""
        if not SUPABASE_AVAILABLE:
            test_logger.warning("Supabase not available - database features disabled")
            return
        
        supabase_url = os.getenv('VITE_SUPABASE_URL')
        supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            test_logger.warning("Supabase credentials not found. Please connect to Supabase first.")
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            test_logger.info("Supabase client initialized successfully")
        except Exception as e:
            test_logger.error(f"Failed to initialize Supabase client: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Supabase client is connected."""
        return self.client is not None
    
    def create_test_run(self, run_id: str, app_type: str, application: Optional[str] = None, 
                       environment: str = "test", test_metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Create a new test run record."""
        if not self.is_connected():
            test_logger.warning("Supabase not connected - skipping test run creation")
            return None
        
        try:
            test_run_data = {
                'run_id': run_id,
                'app_type': app_type,
                'application': application,
                'environment': environment,
                'status': 'running',
                'metadata': test_metadata or {}
            }
            
            result = self.client.table('test_runs').insert(test_run_data).execute()
            
            if result.data:
                test_logger.info(f"Test run created: {run_id}")
                return result.data[0]
            else:
                test_logger.error("Failed to create test run - no data returned")
                return None
                
        except Exception as e:
            test_logger.error(f"Failed to create test run: {str(e)}")
            return None
    
    def update_test_run(self, run_id: str, **kwargs) -> bool:
        """Update test run record."""
        if not self.is_connected():
            test_logger.warning("Supabase not connected - skipping test run update")
            return False
        
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return True
            
            result = self.client.table('test_runs').update(update_data).eq('run_id', run_id).execute()
            
            if result.data:
                test_logger.info(f"Test run updated: {run_id}")
                return True
            else:
                test_logger.warning(f"No test run found to update: {run_id}")
                return False
                
        except Exception as e:
            test_logger.error(f"Failed to update test run: {str(e)}")
            return False
    
    def create_test_execution(self, run_id: str, app_type: str, testcase_name: str, 
                            testcase_description: Optional[str] = None, 
                            test_status: str = 'running', test_duration: Optional[int] = None,
                            application: Optional[str] = None, error_message: Optional[str] = None,
                            stack_trace: Optional[str] = None, screenshot_path: Optional[str] = None,
                            video_path: Optional[str] = None, test_metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Create a new test execution record."""
        if not self.is_connected():
            test_logger.warning("Supabase not connected - skipping test execution creation")
            return None
        
        try:
            execution_data = {
                'run_id': run_id,
                'app_type': app_type,
                'application': application,
                'testcase_name': testcase_name,
                'testcase_description': testcase_description,
                'test_status': test_status,
                'test_duration': test_duration,
                'error_message': error_message,
                'stack_trace': stack_trace,
                'screenshot_path': screenshot_path,
                'video_path': video_path,
                'metadata': test_metadata or {}
            }
            
            result = self.client.table('test_executions').insert(execution_data).execute()
            
            if result.data:
                test_logger.info(f"Test execution created: {testcase_name}")
                return result.data[0]
            else:
                test_logger.error("Failed to create test execution - no data returned")
                return None
                
        except Exception as e:
            test_logger.error(f"Failed to create test execution: {str(e)}")
            return None
    
    def update_test_execution(self, execution_id: str, **kwargs) -> bool:
        """Update test execution record."""
        if not self.is_connected():
            test_logger.warning("Supabase not connected - skipping test execution update")
            return False
        
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return True
            
            result = self.client.table('test_executions').update(update_data).eq('id', execution_id).execute()
            
            if result.data:
                test_logger.info(f"Test execution updated: {execution_id}")
                return True
            else:
                test_logger.warning(f"No test execution found to update: {execution_id}")
                return False
                
        except Exception as e:
            test_logger.error(f"Failed to update test execution: {str(e)}")
            return False
    
    def get_test_run(self, run_id: str) -> Optional[Dict]:
        """Get test run by ID."""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table('test_runs').select('*').eq('run_id', run_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            test_logger.error(f"Failed to get test run: {str(e)}")
            return None
    
    def get_test_executions(self, run_id: str) -> List[Dict]:
        """Get all test executions for a run."""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('test_executions').select('*').eq('run_id', run_id).execute()
            
            return result.data or []
            
        except Exception as e:
            test_logger.error(f"Failed to get test executions: {str(e)}")
            return []
    
    def get_failed_executions(self, run_id: str) -> List[Dict]:
        """Get failed test executions for a run."""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('test_executions').select('*').eq('run_id', run_id).in_('test_status', ['failed', 'error']).execute()
            
            return result.data or []
            
        except Exception as e:
            test_logger.error(f"Failed to get failed executions: {str(e)}")
            return []
    
    def get_test_runs_by_application(self, application: str, limit: int = 50) -> List[Dict]:
        """Get recent test runs for an application."""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('test_runs').select('*').eq('application', application).order('created_at', desc=True).limit(limit).execute()
            
            return result.data or []
            
        except Exception as e:
            test_logger.error(f"Failed to get test runs for application: {str(e)}")
            return []
    
    def get_test_statistics(self, app_type: Optional[str] = None, application: Optional[str] = None, 
                          days: int = 30) -> Dict[str, Any]:
        """Get test execution statistics."""
        if not self.is_connected():
            return {}
        
        try:
            # Build query
            query = self.client.table('test_executions').select('test_status, app_type, application, created_at')
            
            if app_type:
                query = query.eq('app_type', app_type)
            
            if application:
                query = query.eq('application', application)
            
            # Get data from last N days
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            query = query.gte('created_at', cutoff_date)
            
            result = query.execute()
            
            if not result.data:
                return {}
            
            # Calculate statistics
            executions = result.data
            total = len(executions)
            passed = len([e for e in executions if e['test_status'] == 'passed'])
            failed = len([e for e in executions if e['test_status'] == 'failed'])
            skipped = len([e for e in executions if e['test_status'] == 'skipped'])
            error = len([e for e in executions if e['test_status'] == 'error'])
            
            return {
                'total_executions': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'error': error,
                'pass_rate': round((passed / total * 100), 2) if total > 0 else 0,
                'fail_rate': round(((failed + error) / total * 100), 2) if total > 0 else 0,
                'period_days': days
            }
            
        except Exception as e:
            test_logger.error(f"Failed to get test statistics: {str(e)}")
            return {}

# Global Supabase manager instance
supabase_manager = SupabaseManager()