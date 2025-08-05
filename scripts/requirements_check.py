#!/usr/bin/env python3
"""
Requirements checker for Test Automation Framework
Checks if all required dependencies are available
"""

import sys
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_requirement(module_name, description, required=True):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name}: {description}")
        return True
    except ImportError:
        status = "❌" if required else "⚠️ "
        req_text = "REQUIRED" if required else "OPTIONAL"
        print(f"{status} {module_name}: {description} ({req_text})")
        return False

def main():
    """Check all requirements."""
    print("🔍 Checking Test Automation Framework Requirements...\n")
    
    # Core requirements
    print("📦 Core Requirements:")
    core_available = True
    core_available &= check_requirement("pytest", "Testing framework", required=True)
    core_available &= check_requirement("click", "CLI framework", required=True)
    core_available &= check_requirement("pydantic", "Configuration management", required=True)
    core_available &= check_requirement("jinja2", "Template engine for reports", required=True)
    
    print("\n🗄️  Database Requirements:")
    db_available = True
    db_available &= check_requirement("sqlalchemy", "Database ORM", required=True)
    check_requirement("psycopg2", "PostgreSQL adapter", required=False)
    
    print("\n🌐 Web Testing Requirements:")
    check_requirement("playwright", "Web automation", required=False)
    check_requirement("selenium", "Alternative web automation", required=False)
    
    print("\n📱 Mobile Testing Requirements:")
    check_requirement("appium", "Mobile automation", required=False)
    
    print("\n🤖 AI Analysis Requirements:")
    check_requirement("transformers", "NLP models", required=False)
    check_requirement("torch", "PyTorch for ML", required=False)
    check_requirement("sklearn", "Machine learning", required=False)
    check_requirement("nltk", "Natural language processing", required=False)
    
    print("\n☁️  Cloud Integration:")
    check_requirement("supabase", "Supabase client", required=False)
    check_requirement("requests", "HTTP client", required=True)
    
    print("\n📊 Summary:")
    if core_available and db_available:
        print("✅ Core framework is ready to use!")
        print("⚠️  Optional features may be limited based on available dependencies")
    else:
        print("❌ Some core requirements are missing")
        print("Run: pip install -r requirements_minimal.txt")
    
    print("\n🚀 To install missing dependencies:")
    print("   Basic: pip install -r requirements_minimal.txt")
    print("   Full:  pip install -r requirements.txt")
    print("   Web:   playwright install")
    
    return 0 if core_available and db_available else 1

if __name__ == "__main__":
    sys.exit(main())