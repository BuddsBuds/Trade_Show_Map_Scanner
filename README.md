# TradeShow Scout

A tool for automating the extraction of company information and booth details from trade show floor plans.

## Current Development: Phase 1

Phase 1 focuses on core functionality:
- File processing (PDF/Image handling)
- OCR-based text extraction
- Basic web interface for upload and export

For detailed information about Phase 1, see the [Phase 1 Plan](docs/phase-1-plan.md).

## Documentation

- [Product Requirements Document](docs/product-requirements.md) - Overall project objectives and scope
- [Functional Specifications](docs/functional-specifications.md) - Technical specifications
- [Implementation Outline](docs/implementation-outline.md) - System architecture outline
- [Phase 1 Plan](docs/phase-1-plan.md) - Current phase implementation details

## Phase 1 Features

- PDF and image file processing
- Company name and booth size extraction
- Basic web interface for:
  - File upload
  - Results display
  - CSV export

## Tech Stack (Phase 1)

- Backend Services:
  - Python 3.11+
  - FastAPI
  - Tesseract OCR
  - PyPDF2
  - OpenCV
  
- Frontend:
  - React 18+
  - TypeScript
  - Material-UI

## Development

Development follows a strict phase-based approach:
1. Each component must be fully implemented and tested before moving to the next
2. All tests must pass with required coverage
3. Performance benchmarks must be met
4. Documentation is updated based on actual implementation

Current focus is on the File Processing Service implementation. See [Phase 1 Plan](docs/phase-1-plan.md) for detailed development stages and validation criteria.