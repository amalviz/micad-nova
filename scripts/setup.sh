#!/bin/bash

# Test Automation Framework Setup Script
# This script sets up the framework in a new environment

set -e  # Exit on any error

echo "🚀 Setting up Test Automation Framework..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3.8+ is installed
check_python() {
    print_header "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION found"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_header "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Python dependencies..."
    
    # Install basic requirements first
    if [ -f "requirements_minimal.txt" ]; then
        pip install -r requirements_minimal.txt
        print_status "Basic dependencies installed"
    fi
    
    # Install full requirements if available
    if [ -f "requirements.txt" ]; then
        print_warning "Installing full requirements (some may fail in limited environments)..."
        pip install -r requirements.txt || print_warning "Some dependencies failed to install (this is expected in limited environments)"
    fi
    
    # Install Playwright browsers if Playwright is available
    if python3 -c "import playwright" 2>/dev/null; then
        print_status "Installing Playwright browsers..."
        playwright install || print_warning "Playwright browser installation failed"
    else
        print_warning "Playwright not available - web testing will be limited"
    fi
}

# Setup directories
setup_directories() {
    print_header "Creating project directories..."
    
    directories=(
        "logs"
        "reports"
        "screenshots"
        "videos"
        "test_data"
        "config/environments"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created directory: $dir"
    done
}

# Setup environment file
setup_environment() {
    print_header "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file from template"
            print_warning "Please edit .env file with your specific configuration"
        else
            print_warning "No .env.example found, creating basic .env file"
            cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/test_automation

# Supabase Configuration (will be set when you connect)
# VITE_SUPABASE_URL=
# VITE_SUPABASE_ANON_KEY=

# Web Testing Configuration
WEB_BROWSER=chromium
WEB_HEADLESS=false
WEB_TIMEOUT=30000
WEB_BASE_URL=https://example.com

# Mobile Testing Configuration
APPIUM_SERVER_URL=http://localhost:4723
MOBILE_PLATFORM_NAME=Android
MOBILE_DEVICE_NAME=emulator-5554

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# AI Analysis Configuration
ENABLE_AI_ANALYSIS=false

# Reporting Configuration
REPORT_FORMAT=html
ENABLE_SCREENSHOTS=true
ENABLE_VIDEO_RECORDING=false

# General Configuration
PARALLEL_WORKERS=4
RETRY_FAILED_TESTS=1
TEST_TIMEOUT=300
EOF
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Database setup
setup_database() {
    print_header "Setting up database..."
    
    print_status "Database setup options:"
    echo "1. PostgreSQL (recommended for production)"
    echo "2. SQLite (for development/testing)"
    echo "3. Skip database setup"
    
    read -p "Choose option (1-3): " db_choice
    
    case $db_choice in
        1)
            print_status "PostgreSQL selected"
            print_warning "Please ensure PostgreSQL is installed and running"
            print_warning "Update DATABASE_URL in .env file with your PostgreSQL connection string"
            print_status "Example: postgresql://username:password@localhost:5432/test_automation"
            ;;
        2)
            print_status "SQLite selected (will be created automatically)"
            sed -i 's|DATABASE_URL=.*|DATABASE_URL=sqlite:///test_results.db|' .env
            ;;
        3)
            print_warning "Database setup skipped"
            ;;
        *)
            print_warning "Invalid choice, skipping database setup"
            ;;
    esac
}

# Test installation
test_installation() {
    print_header "Testing installation..."
    
    # Test basic import
    if python3 -c "from core.logger import test_logger; print('✓ Core modules working')" 2>/dev/null; then
        print_status "Core modules imported successfully"
    else
        print_error "Core module import failed"
        return 1
    fi
    
    # Test CLI
    if python3 main.py --check &>/dev/null; then
        print_status "CLI working correctly"
    else
        print_warning "CLI test had issues (may be expected in limited environments)"
    fi
    
    # Test database connection
    if python3 -c "from config.database import db_manager; db_manager.create_tables(); print('✓ Database connection working')" 2>/dev/null; then
        print_status "Database connection successful"
    else
        print_warning "Database connection failed (check your DATABASE_URL)"
    fi
}

# Main installation flow
main() {
    print_header "=== Test Automation Framework Setup ==="
    
    check_python
    create_venv
    install_dependencies
    setup_directories
    setup_environment
    setup_database
    test_installation
    
    print_header "=== Setup Complete! ==="
    print_status "Framework installed successfully!"
    
    echo ""
    print_header "Next Steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Set up your database connection"
    echo "3. Connect to Supabase (click button in UI)"
    echo "4. Run tests: python3 -m cli.test_runner --platform web --help"
    echo ""
    print_status "To activate the environment later: source venv/bin/activate"
}

# Run main function
main "$@"