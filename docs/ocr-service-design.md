# TradeShow Scout - OCR Service Technical Design
**Version**: 1.0

## Overview
The OCR Service is responsible for extracting text from preprocessed floor plan images, identifying company names and booth sizes, and providing confidence scores for the extracted information.

## Architecture

### Components

1. **OCR Core**
   ```
   OCRProcessor
   ├── TextExtractor
   │   ├── Tesseract Integration
   │   └── Region Detection
   ├── TextAnalyzer
   │   ├── Company Name Detector
   │   ├── Booth Size Extractor
   │   └── Pattern Matcher
   └── ConfidenceScorer
   ```

2. **Queue System**
   ```
   TaskQueue
   ├── Redis Backend
   ├── Celery Workers
   └── Task Status Tracker
   ```

3. **Result Storage**
   ```
   ResultManager
   ├── PostgreSQL Database
   ├── Cache Layer
   └── Result Retrieval API
   ```

### Data Flow

1. **Image Processing Flow**
   ```mermaid
   graph LR
   A[Preprocessed Image] --> B[Region Detection]
   B --> C[Text Extraction]
   C --> D[Text Analysis]
   D --> E[Results Storage]
   ```

2. **Task Processing Flow**
   ```mermaid
   graph LR
   A[API Request] --> B[Task Queue]
   B --> C[OCR Worker]
   C --> D[Result Storage]
   D --> E[API Response]
   ```

## Component Details

### 1. OCR Core

#### TextExtractor
- **Purpose**: Extract text from image regions
- **Implementation**:
  ```python
  class TextExtractor:
      def extract_text(self, image: Image) -> List[TextRegion]:
          regions = self.detect_regions(image)
          return [self.process_region(r) for r in regions]
  ```

#### TextAnalyzer
- **Purpose**: Analyze extracted text for company names and booth sizes
- **Implementation**:
  ```python
  class TextAnalyzer:
      def analyze(self, text_regions: List[TextRegion]) -> AnalysisResult:
          companies = self.detect_companies(text_regions)
          booth_sizes = self.extract_booth_sizes(text_regions)
          return AnalysisResult(companies, booth_sizes)
  ```

#### ConfidenceScorer
- **Purpose**: Calculate confidence scores for extracted information
- **Implementation**:
  ```python
  class ConfidenceScorer:
      def score(self, analysis_result: AnalysisResult) -> ScoredResult:
          company_scores = self.score_companies(analysis_result.companies)
          size_scores = self.score_booth_sizes(analysis_result.booth_sizes)
          return ScoredResult(company_scores, size_scores)
  ```

### 2. Queue System

#### TaskQueue
- **Purpose**: Manage OCR processing tasks
- **Implementation**:
  ```python
  class TaskQueue:
      def enqueue(self, task: OCRTask) -> str:
          return self.celery_app.send_task('process_ocr', task)
          
      def get_status(self, task_id: str) -> TaskStatus:
          return self.celery_app.AsyncResult(task_id).status
  ```

### 3. Result Storage

#### ResultManager
- **Purpose**: Store and retrieve OCR results
- **Implementation**:
  ```python
  class ResultManager:
      def store_result(self, result: OCRResult) -> str:
          self.cache.set(result.id, result)
          return self.db.insert(result)
          
      def get_result(self, result_id: str) -> OCRResult:
          return self.cache.get(result_id) or self.db.get(result_id)
  ```

## API Endpoints

### OCR Service API
```python
@router.post("/ocr/process")
async def process_image(image_id: str) -> TaskResponse:
    task = queue.enqueue(OCRTask(image_id))
    return TaskResponse(task_id=task.id)

@router.get("/ocr/status/{task_id}")
async def get_status(task_id: str) -> StatusResponse:
    status = queue.get_status(task_id)
    return StatusResponse(status=status)

@router.get("/ocr/result/{task_id}")
async def get_result(task_id: str) -> OCRResult:
    result = result_manager.get_result(task_id)
    return result
```

## Data Models

### Request/Response Models
```python
class OCRTask(BaseModel):
    image_id: str
    parameters: Optional[OCRParameters]

class OCRResult(BaseModel):
    task_id: str
    companies: List[Company]
    booth_sizes: List[BoothSize]
    confidence_scores: ConfidenceScores
    status: ProcessingStatus
```

### Domain Models
```python
class Company(BaseModel):
    name: str
    location: Point
    confidence: float

class BoothSize(BaseModel):
    dimensions: Dimensions
    location: Point
    confidence: float

class ConfidenceScores(BaseModel):
    overall: float
    company_names: float
    booth_sizes: float
```

## Error Handling

### Error Types
1. **OCRError**: Base error for OCR-related issues
2. **RegionDetectionError**: Failed to detect regions in image
3. **TextExtractionError**: Failed to extract text from region
4. **AnalysisError**: Failed to analyze extracted text

### Error Handling Strategy
```python
class OCRErrorHandler:
    def handle_error(self, error: OCRError) -> ErrorResponse:
        match error:
            case RegionDetectionError():
                return self.handle_region_detection_error(error)
            case TextExtractionError():
                return self.handle_text_extraction_error(error)
            case AnalysisError():
                return self.handle_analysis_error(error)
```

## Performance Considerations

### Optimization Strategies
1. **Caching**
   - Cache preprocessed images
   - Cache OCR results
   - Cache analysis results

2. **Parallel Processing**
   - Multiple Celery workers
   - Region-based parallel processing
   - Batch processing optimization

3. **Resource Management**
   - Worker pool sizing
   - Memory management
   - Connection pooling

### Monitoring
1. **Metrics**
   - Processing time per image
   - Accuracy rates
   - Queue length
   - Worker utilization

2. **Alerts**
   - Error rate thresholds
   - Processing time thresholds
   - Queue length thresholds

## Integration Points

### File Processing Service
```python
class FileProcessorIntegration:
    async def get_preprocessed_image(self, image_id: str) -> Image:
        return await file_processor_client.get_image(image_id)
```

### Frontend Integration
```typescript
class OCRClient {
    async processImage(imageId: string): Promise<TaskResponse> {
        return await api.post('/ocr/process', { imageId });
    }

    async getStatus(taskId: string): Promise<StatusResponse> {
        return await api.get(`/ocr/status/${taskId}`);
    }
}
```

## Deployment Considerations

### Requirements
1. **Infrastructure**
   - Redis server
   - PostgreSQL database
   - Celery workers
   - API servers

2. **Configuration**
   - Environment variables
   - Service discovery
   - Load balancing

3. **Scaling**
   - Horizontal scaling of workers
   - Database sharding strategy
   - Cache distribution

### Security
1. **Authentication**
   - Service-to-service auth
   - API key management
   - Token validation

2. **Data Protection**
   - Encryption at rest
   - Secure communication
   - Access control

## Testing Strategy

### Test Types
1. **Unit Tests**
   - Component-level testing
   - Mocked dependencies
   - Error scenarios

2. **Integration Tests**
   - Service integration
   - Database integration
   - Queue system integration

3. **Performance Tests**
   - Load testing
   - Stress testing
   - Endurance testing

### Test Implementation
```python
class OCRServiceTests:
    async def test_process_image(self):
        result = await ocr_service.process_image(test_image)
        assert result.confidence_scores.overall > 0.9

    async def test_error_handling(self):
        with pytest.raises(OCRError):
            await ocr_service.process_image(invalid_image)
```

## Next Steps
1. Set up development environment
2. Implement OCR Core components
3. Set up queue system
4. Implement result storage
5. Create API endpoints
6. Implement monitoring
7. Write tests