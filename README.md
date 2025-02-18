# TradeShow Scout

A tool for automating the extraction of company information and booth details from trade show floor plans.

## Project Status

### Phase 1: File Processing (Completed)
- ✅ File upload and validation
- ✅ Image preprocessing
- ✅ Basic web interface
- ✅ Test coverage: 93%

### Phase 2: OCR Implementation (In Progress)
- ✅ Environment setup (PostgreSQL, Redis, Tesseract)
- ✅ Service dependency configuration
- ✅ Base service implementation
- 🔄 OCR text extraction
- 🔄 Company name detection
- 🔄 Booth size analysis
- 🔄 Enhanced web interface

See [Phase 2 Plan](docs/phase-2-plan.md) for detailed implementation strategy.

## Documentation

- [Product Requirements Document](docs/product-requirements.md) - Project objectives and scope
- [Functional Specifications](docs/functional-specifications.md) - Technical specifications
- [Implementation Outline](docs/implementation-outline.md) - System architecture
- [Phase 1 Plan](docs/phase-1-plan.md) - File processing implementation
- [Phase 2 Plan](docs/phase-2-plan.md) - OCR implementation strategy
- [OCR Service Specification](docs/ocr-service-specification.md) - OCR service design

## Tech Stack

### Current Implementation
- Frontend: React SPA with drag-and-drop upload
- Backend: Python/FastAPI
- Image Processing: PIL, OpenCV
- OCR: Tesseract OCR
- Queue System: Redis/Celery
- Database: PostgreSQL
- Testing: pytest with 93% coverage

## Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Tesseract OCR 5+
- Virtual environment

### Setup
```bash
# File Processor Service
cd services/file-processor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OCR Service
cd ../ocr-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest

# Start services
python src/main.py  # In each service directory
```

## Project Structure
```
trade-show-scout/
├── docs/                    # Documentation
├── services/               
│   ├── file-processor/     # File Processing Service
│   │   ├── src/
│   │   │   ├── api/        # FastAPI endpoints
│   │   │   ├── core/       # Core processing
│   │   │   ├── utils/      # Utilities
│   │   │   └── tests/      # Test suite
│   │   └── requirements.txt
│   └── ocr-service/        # OCR Processing Service
│       ├── src/
│       │   ├── api/        # FastAPI endpoints
│       │   ├── core/       # OCR processing
│       │   ├── config/     # Configuration
│       │   ├── utils/      # Utilities
│       │   └── tests/      # Test suite
│       ├── config/         # Environment configs
│       └── requirements.txt
```

## Contributing
1. Ensure all tests pass before submitting changes
2. Follow the phase-based development approach
3. Maintain test coverage above 90%
4. Update documentation as needed

## Next Steps
1. ✅ Set up OCR development environment
2. ✅ Configure service dependencies
3. ✅ Implement base service setup
4. 🔄 Implement core OCR functionality
5. 🔄 Develop integration layer
6. 🔄 Create enhanced UI components