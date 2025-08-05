from setuptools import setup, find_packages

setup(
    name="test-automation-framework",
    version="1.0.0",
    author="Test Automation Team",
    description="Comprehensive Python test automation framework for web and mobile",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "appium-python-client>=3.1.0",
        "pytest>=7.4.3",
        "pytest-html>=4.1.1",
        "loguru>=0.7.2",
        "sqlalchemy>=2.0.23",
        "click>=8.1.7",
        "pydantic>=2.5.0",
        "transformers>=4.36.0",
        "scikit-learn>=1.3.2",
    ],
    entry_points={
        "console_scripts": [
            "test-runner=cli.test_runner:main",
        ],
    },
)