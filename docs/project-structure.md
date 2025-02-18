# TradeShow Scout - Project Structure

## Repository Organization

```
trade-show-scout/
├── docs/                          # Documentation
├── services/                      # Microservices
│   ├── file-processor/           # File Processing Service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── api/             # FastAPI endpoints
│   │   │   ├── core/            # Core processing logic
│   │   │   ├── utils/           # Utility functions
│   │   │   └── tests/           # Unit tests
│   │   └── docker-compose.yml
│   │
│   ├── ocr-service/             # OCR Service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── utils/
│   │   │   └── tests/
│   │   └── docker-compose.yml
│   │
│   ├── contact-scraper/         # Contact Scraping Service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── utils/
│   │   │   └── tests/
│   │   └── docker-compose.yml
│   │
│   └── frontend/                # Frontend Service
│       ├── Dockerfile
│       ├── package.json
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   ├── utils/
│       │   └── tests/
│       └── docker-compose.yml
│
├── infrastructure/              # Infrastructure Configuration
│   ├── kubernetes/             # K8s configurations
│   │   ├── development/
│   │   └── production/
│   ├── monitoring/             # Monitoring setup
│   │   ├── prometheus/
│   │   └── grafana/
│   └── ci-cd/                  # CI/CD configurations
│
├── scripts/                    # Development and deployment scripts
│   ├── setup.sh
│   ├── build.sh
│   └── deploy.sh
│
└── docker-compose.yml          # Root compose file for local development
```

## Service Details

### File Processing Service
- FastAPI for REST API
- Celery for async processing
- OpenCV for image processing
- PyPDF2 for PDF handling

### OCR Service
- FastAPI for REST API
- Tesseract OCR integration
- Custom text processing algorithms
- Confidence scoring system

### Contact Scraping Service
- FastAPI for REST API
- Hunter.io API integration
- LinkedIn API integration
- Rate limiting and queueing

### Frontend Service
- React with TypeScript
- Material-UI components
- Redux for state management
- Jest for testing

## Development Setup

1. **Local Development**
   ```bash
   # Start all services
   docker-compose up -d

   # Start specific service
   docker-compose up file-processor -d
   ```

2. **Service Development**
   ```bash
   # Enter service directory
   cd services/file-processor

   # Install dependencies
   pip install -r requirements.txt

   # Run tests
   pytest
   ```

## Next Steps

1. Create base service templates
2. Set up development environment
3. Implement core infrastructure
4. Begin service development