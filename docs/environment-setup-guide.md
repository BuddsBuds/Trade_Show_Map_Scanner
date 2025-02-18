# TradeShow Scout - Development Environment Setup Guide
**Version**: 1.0

## Overview
This guide provides step-by-step instructions for setting up the development environment for Phase 2 OCR service implementation.

## Prerequisites

### Required Software
1. **Python Environment**
   - Python 3.11+
   - pip
   - virtualenv or conda

2. **Database**
   - PostgreSQL 14+
   - pgAdmin 4 (optional)

3. **Message Queue**
   - Redis 7+
   - Redis Commander (optional)

4. **OCR Engine**
   - Tesseract OCR 5.0+
   - Required language packs

5. **Development Tools**
   - Git
   - VSCode or preferred IDE
   - Docker Desktop
   - Postman or similar API testing tool

## Installation Steps

### 1. Python Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. PostgreSQL Setup
```bash
# macOS (using Homebrew)
brew install postgresql@14
brew services start postgresql@14

# Ubuntu
sudo apt-get update
sudo apt-get install postgresql-14

# Windows
# Download installer from https://www.postgresql.org/download/windows/

# Create database
createdb tradeshowscout_dev
createdb tradeshowscout_test
```

### 3. Redis Setup
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# Download from https://redis.io/download
```

### 4. Tesseract OCR Setup
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### 5. Docker Setup
```bash
# Pull required images
docker pull redis:7
docker pull postgres:14
docker pull python:3.11-slim
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the project root:
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tradeshowscout_dev
DB_USER=your_username
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# OCR
TESSERACT_PATH=/usr/local/bin/tesseract  # Adjust for your OS

# API
API_PORT=8000
DEBUG=true
```

### 2. Database Configuration
```sql
-- Connect to PostgreSQL
psql tradeshowscout_dev

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 3. Redis Configuration
Update redis.conf:
```conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Project Structure Setup
```bash
# Create required directories
mkdir -p services/ocr-service/src/{api,core,utils,tests}
mkdir -p services/ocr-service/data/{uploads,processed}
```

## Verification Steps

### 1. Database Connection
```python
import psycopg2

conn = psycopg2.connect(
    dbname="tradeshowscout_dev",
    user="your_username",
    password="your_password",
    host="localhost"
)
```

### 2. Redis Connection
```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0
)
```

### 3. Tesseract OCR
```python
import pytesseract

print(pytesseract.get_tesseract_version())
```

## Development Workflow

### 1. Starting Services
```bash
# Start PostgreSQL
pg_ctl start

# Start Redis
redis-server

# Start development server
python src/main.py
```

### 2. Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

### 3. Code Quality
```bash
# Run linter
flake8 src

# Run type checker
mypy src
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Issues**
   - Check service status
   - Verify credentials
   - Check port availability

2. **Redis Connection Issues**
   - Verify Redis is running
   - Check port conflicts
   - Review memory settings

3. **Tesseract OCR Issues**
   - Verify installation path
   - Check language pack installation
   - Test with sample images

## Next Steps

1. Verify all components are installed and configured
2. Run the verification steps
3. Create a test file upload
4. Process a sample image through OCR
5. Begin implementation of core services

## Support

For development environment issues:
1. Check the troubleshooting guide
2. Review logs in `logs/` directory
3. Contact technical lead

## Maintenance

### Regular Tasks
1. Update dependencies monthly
2. Review and clean Redis cache
3. Backup development database
4. Update documentation as needed

### Security
1. Keep all components updated
2. Use secure credentials
3. Don't commit sensitive data
4. Follow security best practices

Remember to update this guide as new requirements or issues are discovered during development.