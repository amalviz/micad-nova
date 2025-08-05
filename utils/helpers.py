"""
Helper utilities for test automation framework.
"""
import json
import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from core.logger import test_logger

class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_email(domain: str = "example.com") -> str:
        """Generate random email address."""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_password(length: int = 12, include_special: bool = True) -> str:
        """Generate random password."""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*"
        
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def generate_phone_number(country_code: str = "+1") -> str:
        """Generate random phone number."""
        area_code = ''.join(random.choices(string.digits, k=3))
        exchange = ''.join(random.choices(string.digits, k=3))
        number = ''.join(random.choices(string.digits, k=4))
        return f"{country_code} ({area_code}) {exchange}-{number}"
    
    @staticmethod
    def generate_name() -> Dict[str, str]:
        """Generate random first and last names."""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Mary"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        
        return {
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names)
        }
    
    @staticmethod
    def generate_address() -> Dict[str, str]:
        """Generate random address."""
        streets = ["Main St", "Oak Ave", "Pine Rd", "Elm St", "Maple Ave"]
        cities = ["Springfield", "Franklin", "Georgetown", "Madison", "Arlington"]
        states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
        
        return {
            "street": f"{random.randint(100, 9999)} {random.choice(streets)}",
            "city": random.choice(cities),
            "state": random.choice(states),
            "zip_code": f"{random.randint(10000, 99999)}"
        }

class FileHelper:
    """File manipulation utilities."""
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """Read JSON file."""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                test_logger.step(f"Read JSON file: {file_path}")
                return data
        except Exception as e:
            test_logger.error(f"Failed to read JSON file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any]):
        """Write data to JSON file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2, default=str)
                test_logger.step(f"Wrote JSON file: {file_path}")
        except Exception as e:
            test_logger.error(f"Failed to write JSON file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def read_text(file_path: str) -> str:
        """Read text file."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                test_logger.step(f"Read text file: {file_path}")
                return content
        except Exception as e:
            test_logger.error(f"Failed to read text file {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def write_text(file_path: str, content: str):
        """Write content to text file."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
                test_logger.step(f"Wrote text file: {file_path}")
        except Exception as e:
            test_logger.error(f"Failed to write text file {file_path}: {str(e)}")
            raise

class DateTimeHelper:
    """Date and time utilities."""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
    
    @staticmethod
    def get_formatted_date(format_str: str = "%Y-%m-%d") -> str:
        """Get current date in specified format."""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def get_future_date(days: int = 30, format_str: str = "%Y-%m-%d") -> str:
        """Get future date."""
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime(format_str)
    
    @staticmethod
    def get_past_date(days: int = 30, format_str: str = "%Y-%m-%d") -> str:
        """Get past date."""
        past_date = datetime.now() - timedelta(days=days)
        return past_date.strftime(format_str)

class StringHelper:
    """String manipulation utilities."""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID string."""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_random_string(length: int = 10, chars: str = None) -> str:
        """Generate random string."""
        if chars is None:
            chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to slug format."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

class WaitHelper:
    """Wait and polling utilities."""
    
    @staticmethod
    def wait_until(condition_func, timeout: int = 30, poll_interval: float = 0.5) -> bool:
        """Wait until condition is met."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception:
                pass
            
            time.sleep(poll_interval)
        
        return False
    
    @staticmethod
    def retry_on_exception(func, max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
        """Retry function on exception."""
        import time
        
        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                if attempt == max_attempts - 1:
                    raise e
                
                test_logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                time.sleep(delay)

class ConfigHelper:
    """Configuration utilities."""
    
    @staticmethod
    def get_environment_config(env_name: str) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        config_file = Path(__file__).parent.parent / "config" / f"{env_name}.json"
        
        if config_file.exists():
            return FileHelper.read_json(str(config_file))
        else:
            test_logger.warning(f"Environment config not found: {env_name}")
            return {}
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries."""
        merged = {}
        for config in configs:
            merged.update(config)
        return merged