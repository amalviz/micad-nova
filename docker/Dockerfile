# Test Automation Framework Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements*.txt ./
COPY setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install --with-deps chromium firefox webkit

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports screenshots videos test_data

# Set permissions
RUN chmod +x scripts/*.sh scripts/*.py

# Install the framework
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 testuser && chown -R testuser:testuser /app
USER testuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python main.py --check || exit 1

# Default command
CMD ["python", "-m", "cli.test_runner", "--help"]