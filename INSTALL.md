# Installation Guide

This guide will help you install and set up the Test Automation Framework in a new environment with a new database.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the project
git clone <repository-url>
cd test-automation-framework

# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: Manual Setup

Follow the detailed steps below for manual installation.

## 📋 Prerequisites

- **Python 3.8+** (required)
- **PostgreSQL 12+** (recommended) or SQLite (for development)
- **Git** (for cloning)
- **Node.js 16+** (optional, for Playwright)

## 🔧 Step-by-Step Installation

### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install minimal requirements (works in most environments)
pip install -r requirements_minimal.txt

# Install full requirements (optional, some may fail in limited environments)
pip install -r requirements.txt
```

### 3. Install Playwright (for Web Testing)

```bash
# Install Playwright browsers (if Playwright is available)
playwright install
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

### 5. Database Setup

#### Option A: PostgreSQL (Recommended)

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE test_automation;
CREATE USER testuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE test_automation TO testuser;
\q

# Update .env file
DATABASE_URL=postgresql://testuser:your_password@localhost:5432/test_automation
```

#### Option B: SQLite (Development)

```bash
# Update .env file
DATABASE_URL=sqlite:///test_results.db
```

### 6. Initialize Database

```bash
# Initialize database tables
python scripts/database_setup.py init

# Check database connection
python scripts/database_setup.py check
```

### 7. Create Project Directories

```bash
# Create necessary directories
mkdir -p logs reports screenshots videos test_data config/environments
```

### 8. Verify Installation

```bash
# Test the installation
python main.py --check

# Test CLI
python -m cli.test_runner --help
```

## 🗄️ Database Configuration

### PostgreSQL Setup (Detailed)

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib
   
   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create Database**:
   ```sql
   -- Connect as postgres user
   sudo -u postgres psql
   
   -- Create database and user
   CREATE DATABASE test_automation;
   CREATE USER testuser WITH ENCRYPTED PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE test_automation TO testuser;
   
   -- Grant schema permissions
   \c test_automation
   GRANT ALL ON SCHEMA public TO testuser;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO testuser;
   
   \q
   ```

3. **Update Configuration**:
   ```bash
   # In .env file
   DATABASE_URL=postgresql://testuser:secure_password@localhost:5432/test_automation
   ```

### Database Management Commands

```bash
# Initialize database
python scripts/database_setup.py init

# Check database status
python scripts/database_setup.py check

# View database statistics
python scripts/database_setup.py stats

# Clean up old records (older than 30 days)
python scripts/database_setup.py cleanup --days 30

# Force recreate tables
python scripts/database_setup.py init --force
```

## 🔗 Supabase Integration

## 🗄️ Database Integration

The framework uses PostgreSQL as the primary database for storing test results:

1. **Database Setup**: Follow the PostgreSQL setup instructions above
2. **Schema Creation**: Tables are automatically created on first run
3. **Test Tracking**: All test executions are automatically tracked

## 🧪 Running Tests

### Basic Usage

```bash
# Run web tests
python -m cli.test_runner --platform web --app myapp

# Run mobile tests
python -m cli.test_runner --platform mobile --app myapp

# Run with AI analysis
python -m cli.test_runner --platform web --ai-analysis

# Generate reports
python -m cli.test_runner report --run-id <run-id> --format html
```

### Advanced Options

```bash
# Parallel execution
python -m cli.test_runner --platform web --parallel 4

# Headless mode
python -m cli.test_runner --platform web --headless

# Custom browser
python -m cli.test_runner --platform web --browser firefox

# Retry failed tests
python -m cli.test_runner --platform web --retry 2
```

## 📁 Project Structure

```
test-automation-framework/
├── config/                 # Configuration files
├── core/                   # Core framework components
├── page_objects/           # Page objects and screen objects
├── tests/                  # Test cases by application
│   ├── web/               # Web tests
│   └── mobile/            # Mobile tests
├── utils/                  # Utilities and helpers
├── cli/                    # Command-line interface
├── scripts/               # Setup and utility scripts
├── logs/                  # Log files
├── reports/               # Generated reports
├── screenshots/           # Test screenshots
└── videos/                # Test recordings
```

## 🔧 Configuration Files

### .env Configuration

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/test_automation

# Supabase (set automatically when connecting)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=

# Web Testing
WEB_BROWSER=chromium
WEB_HEADLESS=false
WEB_BASE_URL=https://your-app.com

# Mobile Testing
APPIUM_SERVER_URL=http://localhost:4723
MOBILE_PLATFORM_NAME=Android
MOBILE_DEVICE_NAME=emulator-5554

# Features
ENABLE_AI_ANALYSIS=false
ENABLE_SCREENSHOTS=true
ENABLE_VIDEO_RECORDING=false

# Performance
PARALLEL_WORKERS=4
TEST_TIMEOUT=300
```

## 🚨 Troubleshooting

### Common Issues

1. **Python Import Errors**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements_minimal.txt
   ```

2. **Database Connection Issues**:
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Test connection manually
   psql -h localhost -U testuser -d test_automation
   
   # Check database setup
   python scripts/database_setup.py check
   ```

3. **Playwright Issues**:
   ```bash
   # Reinstall Playwright browsers
   playwright install
   
   # Check Playwright installation
   playwright --version
   ```

4. **Permission Issues**:
   ```bash
   # Fix script permissions
   chmod +x scripts/setup.sh
   
   # Fix directory permissions
   chmod -R 755 logs reports screenshots
   ```

### Environment-Specific Notes

- **WebContainer**: Some features may be limited (Playwright, Appium)
- **Docker**: Use appropriate base images with required dependencies
- **CI/CD**: Set environment variables in your pipeline configuration

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python main.py --check` to see available components
3. Check logs in the `logs/` directory
4. Verify database connection with `python scripts/database_setup.py check`

## 🎯 Next Steps

After installation:

1. **Configure your applications**: Add test cases in `tests/web/` or `tests/mobile/`
2. **Set up page objects**: Create page objects in `page_objects/`
3. **Configure environments**: Add environment-specific configs
4. **Set up CI/CD**: Integrate with your deployment pipeline
5. **Enable monitoring**: Connect to Supabase for real-time tracking

Happy testing! 🚀