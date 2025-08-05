"""
Main entry point for the test automation framework.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from cli.test_runner import cli
from core.logger import get_logger
from config.settings import get_settings

# Try to import optional dependencies
try:
    import asyncio
except ImportError:
    asyncio = None

logger = get_logger(__name__)

def main():
    """Main function to run the CLI."""
    try:
        logger.info("Starting Test Automation Framework")
        logger.info("Note: Running in WebContainer with limited Python environment")
        cli()
    except KeyboardInterrupt:
        logger.info("Framework interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Framework error: {e}")
        sys.exit(1)

def check_environment():
    """Check what components are available in the current environment."""
    settings = get_settings()
    
    print("=== Test Automation Framework Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Project root: {Path(__file__).parent}")
    
    # Check for optional dependencies
    optional_deps = {
        'playwright': 'Web automation with Playwright',
        'appium': 'Mobile automation with Appium', 
        'transformers': 'AI-based failure analysis',
        'sklearn': 'Machine learning features',
        'nltk': 'Natural language processing'
    }
    
    print("\n=== Available Components ===")
    for dep, description in optional_deps.items():
        try:
            __import__(dep)
            print(f"✓ {dep}: {description}")
        except ImportError:
            print(f"✗ {dep}: {description} (not available)")
    
    print(f"\n=== Configuration ===")
    print(f"Environment: {settings.environment}")
    print(f"Log level: {settings.log_level}")
    print(f"Database URL: {settings.database_url}")
    
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_environment()
    else:
        main()