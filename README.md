# Test Automation Framework

A comprehensive Python-based test automation framework supporting both web and mobile applications with advanced features including AI-powered failure analysis.

## 🚀 Supabase Integration

This framework integrates with Supabase to track all test executions with detailed information:
- **App Type**: Web or Mobile application testing
- **Application**: Specific application being tested
- **Test Case Name**: Full test identifier (class.method)
- **Test Case Description**: Extracted from test docstrings
- **Test Status**: passed, failed, skipped, or error
- **Test Duration**: Execution time in milliseconds
- **Error Details**: Full error messages and stack traces
- **Screenshots & Videos**: Captured media for failed tests

### Setup Supabase Connection

1. Click the "Connect to Supabase" button in the top right
2. The database schema will be automatically created
3. All test executions will be tracked in real-time

## Features

- **Multi-Platform Support**: Web (Playwright) and Mobile (Appium) testing
- **Modular Architecture**: Organized by application with clear separation of concerns
- **CLI Interface**: Command-line tool for easy test execution
- **Object Repository**: Structured page objects and screen objects
- **Advanced Logging**: Comprehensive logging with multiple output formats
- **Database Integration**: Store and retrieve test results
- **AI-Powered Analysis**: NLP/ML-based failure analysis and insights
- **Rich Reporting**: HTML, Allure, and custom report generation

## Quick Start

### Automated Installation

```bash
# Clone the repository
git clone <repository-url>
cd test-automation-framework

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Installation

```bash
# Install dependencies
python3 -m pip install -r requirements_minimal.txt
```

### Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

### Running Tests

```bash
# Run all tests
python main.py --platform web --app myapp

# Run specific application tests
python main.py --app my-app --platform mobile

# Run with AI analysis
python main.py --platform web --ai-analysis

# Using CLI tool
python -m cli.test_runner --help
```

## Project Structure

```
├── config/           # Configuration files
├── core/            # Core framework components
├── page_objects/    # Page objects and screen objects
├── tests/           # Test cases organized by application
├── utils/           # Utilities and helpers
├── cli/             # Command-line interface
├── reports/         # Generated reports
└── main.py          # Main entry point
```

## Writing Tests

### Web Tests

```python
from tests.web.base_web_test import BaseWebTest
from page_objects.web.login_page import LoginPage

class TestLogin(BaseWebTest):
    async def test_valid_login(self):
        """Test successful login with valid credentials."""
        login_page = LoginPage(self.page)
        login_page.login("user@example.com", "password")
        assert login_page.is_logged_in()
```

### Mobile Tests

```python
from tests.mobile.base_mobile_test import BaseMobileTest
from page_objects.mobile.login_screen import LoginScreen

class TestMobileLogin(BaseMobileTest):
    def test_valid_login(self):
        """Test successful mobile login."""
        login_screen = LoginScreen(self.driver)
        login_screen.login("user@example.com", "password")
        assert login_screen.is_logged_in()
```

## Configuration

The framework uses environment variables and configuration files:

- `.env` - Environment-specific settings
- Supabase connection via environment variables (auto-configured)
- PostgreSQL database for local test result storage
- `config/settings.py` - Framework configuration
- `config/database.py` - Database configuration

### Database Setup

The framework supports PostgreSQL as the primary database with SQLite fallback:

```bash
# PostgreSQL (recommended)
DATABASE_URL=postgresql://username:password@localhost:5432/test_automation

# SQLite fallback (automatic if PostgreSQL unavailable)
DATABASE_URL=sqlite:///test_results.db
```
## AI-Powered Analysis

The framework includes optional AI-based failure analysis that can:

- Analyze error messages and stack traces
- Categorize failure types
- Suggest potential fixes
- Identify patterns in test failures

Enable AI analysis with the `--ai-analysis` flag or set `ENABLE_AI_ANALYSIS=true` in your environment.

## Database Schema

### Test Runs Table
- Tracks overall test execution sessions
- Groups related test cases by run_id
- Stores summary statistics and metadata

### Test Executions Table  
- Individual test case results
- Detailed execution information
- Links to screenshots and videos
- Error messages and stack traces

All data is automatically synced to Supabase during test execution.
## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.