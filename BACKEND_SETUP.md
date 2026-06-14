# AjiTkhdem Backend Setup & Execution Guide

## Overview
The backend consists of three main services in the data-pipeline:
1. **Ingestion** - Web scraping service (Indeed, Rekrute)
2. **Normalization** - Data standardization and processing
3. **Pre-processing** - Data cleaning and validation

All services use Python virtual environments (`venv`) for dependency isolation and pytest for testing with proper PYTHONPATH configuration.

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- pip & venv (included with Python)

## Option 1: Running with Docker Compose (Recommended)

### Start All Services
```bash
cd backend/services
docker-compose up -d
```

This will start all three services and their dependencies:
- Redis (for Ingestion)
- PostgreSQL (for Normalization)
- Kafka & Zookeeper (for Normalization)
- MongoDB (for Pre-processing)

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ingestion
docker-compose logs -f normalization
docker-compose logs -f preprocessing
```

### Stop Services
```bash
docker-compose down
```

## Option 2: Running Locally with Virtual Environments (Development)

### Quick Setup (Automated)

#### Linux/macOS:
```bash
# Ingestion Service
cd backend/services/data-pipeline/ingestion
bash setup.sh

# Normalization Service
cd backend/services/data-pipeline/noramlization
bash setup.sh

# Pre-processing Service
cd backend/services/data-pipeline/pre-processing
bash setup.sh
```

#### Windows:
```bash
# Ingestion Service
cd backend\services\data-pipeline\ingestion
setup.bat

# Normalization Service
cd backend\services\data-pipeline\noramlization
setup.bat

# Pre-processing Service
cd backend\services\data-pipeline\pre-processing
setup.bat
```

### Manual Setup (Step-by-Step)

#### 1. Set Up Virtual Environments

For each service (ingestion, normalization, pre-processing):

**Linux/macOS:**
```bash
cd backend/services/data-pipeline/<service-name>
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Windows:**
```bash
cd backend\services\data-pipeline\<service-name>
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 2. Set Up Environment Variables
Create `.env` files in each service directory:

#### `backend/services/data-pipeline/ingestion/.env`
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
```

#### `backend/services/data-pipeline/noramlization/.env`
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
LOG_LEVEL=INFO
```

#### `backend/services/data-pipeline/pre-processing/.env`
```
MONGODB_URL=mongodb://localhost:27017
MONGO_DB_NAME=job_preprocessing
LOG_LEVEL=INFO
```

#### 3. Start Required Services

```bash
# Install Docker if not already installed

# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=job_db \
  -p 5432:5432 \
  postgres:15-alpine

# Start MongoDB
docker run -d --name mongodb \
  -p 27017:27017 \
  mongo:7

# Start Kafka (requires Zookeeper)
docker run -d --name zookeeper \
  -e ZOOKEEPER_CLIENT_PORT=2181 \
  -p 2181:2181 \
  confluentinc/cp-zookeeper:7.5.0

docker run -d --name kafka \
  -e KAFKA_BROKER_ID=1 \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  -p 9092:9092 \
  confluentinc/cp-kafka:7.5.0
```

#### 4. Run Each Service

**All services should have their virtual environment activated before running:**

#### Ingestion Service
```bash
cd backend/services/data-pipeline/ingestion
source venv/bin/activate  # On Windows: venv\Scripts\activate
python src/main.py
```

#### Normalization Service
```bash
cd backend/services/data-pipeline/noramlization
source venv/bin/activate  # On Windows: venv\Scripts\activate
python src/main.py
```

#### Pre-processing Service
```bash
cd backend/services/data-pipeline/pre-processing
source venv/bin/activate  # On Windows: venv\Scripts\activate
python src/main.py
```

## Running Tests

Tests are configured with `pytest.ini` files that automatically set the `src` directory in PYTHONPATH.

### Ingestion Service Tests
```bash
cd backend/services/data-pipeline/ingestion
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest test/ -v
```

### Normalization Service Tests
```bash
cd backend/services/data-pipeline/noramlization
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest test/unit_test/ -v
```

### Pre-processing Service Tests
```bash
cd backend/services/data-pipeline/pre-processing
source venv/bin/activate  # On Windows: venv\Scripts\activate
pytest test/unit-test/ -v
```

### Specific Test File
```bash
cd backend/services/data-pipeline/ingestion
source venv/bin/activate
pytest test/test_indeed_scraper.py -v
```

### All Tests with Coverage
```bash
cd backend/services/data-pipeline/ingestion
source venv/bin/activate
pip install pytest-cov
pytest test/ --cov=src --cov-report=html
```

## Virtual Environment Management

### Why Virtual Environments?
- **Isolation**: Each service has independent dependencies
- **Reproducibility**: Exact versions specified in `requirements.txt`
- **No conflicts**: Multiple Python projects won't interfere
- **CI/CD compatibility**: Same setup works locally and in GitHub Actions

### Common venv Commands

**Activate (Linux/macOS):**
```bash
source venv/bin/activate
```

**Activate (Windows):**
```bash
venv\Scripts\activate.bat
```

**Deactivate (All platforms):**
```bash
deactivate
```

**View installed packages:**
```bash
pip list
```

**Update requirements.txt:**
```bash
pip freeze > requirements.txt
```

## Troubleshooting

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### PostgreSQL Connection Error
```bash
# Check connection
psql -h localhost -U postgres -d job_db
# Enter password: postgres
```

### MongoDB Connection Error
```bash
# Check connection
mongosh mongodb://localhost:27017
```

### Kafka Issues
```bash
# Check if Kafka is running
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### ModuleNotFoundError with pytest
If tests fail with `ModuleNotFoundError`, ensure:
1. Virtual environment is activated
2. You're in the service directory (where pytest.ini exists)
3. Requirements are installed: `pip install -r requirements.txt`
4. Run: `pytest test/ -v`

### Import Issues in Tests
The `pytest.ini` file automatically sets `src` directory in PYTHONPATH. If you still have import issues:
```bash
# Set PYTHONPATH manually
export PYTHONPATH="${PWD}/src:$PYTHONPATH"  # Linux/macOS
set PYTHONPATH=%CD%\src;%PYTHONPATH%        # Windows
pytest test/ -v
```

## Frontend Execution

Since the frontend is already running:
```bash
cd frontend
npm run dev
```

## Quick Start Checklist (Local Development)
- [ ] Clone the repository
- [ ] Install Docker & Docker Compose
- [ ] Start Docker containers: `docker run -d --name redis -p 6379:6379 redis:7-alpine` (and others)
- [ ] For each service: Run `bash setup.sh` (Linux/macOS) or `setup.bat` (Windows)
- [ ] Create `.env` files with required variables
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Run service: `python src/main.py`
- [ ] Run tests: `pytest test/ -v`
- [ ] Frontend: `npm run dev` in `frontend/` directory
- [ ] Frontend should be running on `http://localhost:5173` (Vite default)

## GitHub Actions CI/CD Pipeline

The workflow automatically runs all tests on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### What's Tested:
- **Ingestion service tests** (with Redis service)
  - Python 3.11 + venv + requirements.txt
  - PYTHONPATH configured via pytest.ini
  
- **Normalization service tests** (with PostgreSQL, Kafka, Zookeeper)
  - Python 3.11 + venv + requirements.txt
  - PYTHONPATH configured via pytest.ini
  
- **Pre-processing service tests** (with MongoDB)
  - Python 3.11 + venv + requirements.txt
  - PYTHONPATH configured via pytest.ini
  
- **Frontend build & lint** (Node.js 22)
  - npm ci for reproducible installs
  - TypeScript lint check
  
- **Docker image builds** (main branch only)
  - All three service images built and validated

### Fixes Applied:
✅ **Node.js updated** from 18 to 22 (Vite requirement: 20.19+ or 22.12+)
✅ **Python paths fixed** - PYTHONPATH set to `src` directory in each service
✅ **venv configured** - Virtual environments created and activated in CI/CD
✅ **pytest.ini added** - PYTHONPATH configuration for each service
✅ **__init__.py added** - Test directories properly configured as packages
✅ **pip dependencies** - All packages installed via requirements.txt in venv
