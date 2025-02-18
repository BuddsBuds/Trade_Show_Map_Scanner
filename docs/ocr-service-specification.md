# TradeShow Scout - OCR Service Technical Specification
**Version**: 1.0

## Service Components

### 1. OCR Core Module
```python
class OCRProcessor:
    """Core OCR processing engine"""
    
    def __init__(self, config: OCRConfig):
        self.tesseract = TesseractWrapper(config)
        self.preprocessor = ImagePreprocessor()
        self.analyzer = TextAnalyzer()
        self.validator = ResultValidator()

    async def process_image(self, image: Image) -> OCRResult:
        """Main processing pipeline"""
        preprocessed = await self.preprocessor.prepare(image)
        text = await self.tesseract.extract_text(preprocessed)
        analysis = await self.analyzer.analyze(text)
        validated = await self.validator.validate(analysis)
        return validated
```

### 2. Image Preprocessing
```python
class ImagePreprocessor:
    """Image preprocessing for optimal OCR"""
    
    async def prepare(self, image: Image) -> Image:
        """Prepare image for OCR processing"""
        return await self._pipeline([
            self._normalize,
            self._enhance_contrast,
            self._remove_noise,
            self._deskew,
            self._detect_regions
        ])

    async def _detect_regions(self, image: Image) -> List[Region]:
        """Detect booth regions in floor plan"""
        return [
            Region(bbox, confidence)
            for bbox, confidence in self._find_booths(image)
        ]
```

### 3. Text Analysis
```python
class TextAnalyzer:
    """Analyze extracted text for company info"""
    
    async def analyze(self, text: str) -> AnalysisResult:
        """Extract company names and booth info"""
        companies = await self._extract_companies(text)
        booths = await self._extract_booth_info(text)
        return AnalysisResult(
            companies=companies,
            booths=booths,
            confidence=self._calculate_confidence()
        )

    async def _extract_companies(self, text: str) -> List[Company]:
        """Extract company names using pattern matching"""
        patterns = [
            r'Company:\s*([A-Za-z0-9\s&]+)',
            r'Booth:\s*([A-Za-z0-9\s&]+)',
            r'^([A-Z][A-Za-z0-9\s&]+)$'
        ]
        return self._match_patterns(text, patterns)
```

### 4. Queue Management
```python
class OCRQueue:
    """Manage OCR processing queue"""
    
    def __init__(self, redis_config: RedisConfig):
        self.redis = Redis(redis_config)
        self.celery = Celery(broker=redis_config.url)

    async def enqueue(self, task: OCRTask) -> str:
        """Add task to processing queue"""
        task_id = await self._generate_task_id()
        await self.redis.set(f"task:{task_id}", task.json())
        return task_id

    async def process_next(self) -> Optional[OCRResult]:
        """Process next task in queue"""
        task = await self.redis.get_next_task()
        if task:
            return await self._process_task(task)
        return None
```

### 5. Result Storage
```python
class ResultManager:
    """Manage OCR results storage"""
    
    def __init__(self, db_config: DBConfig):
        self.db = PostgresDB(db_config)
        self.cache = RedisCache(db_config.redis_url)

    async def store_result(self, result: OCRResult) -> str:
        """Store OCR result"""
        result_id = await self.db.insert_result(result)
        await self.cache.set(f"result:{result_id}", result)
        return result_id

    async def get_result(self, result_id: str) -> Optional[OCRResult]:
        """Retrieve OCR result"""
        cached = await self.cache.get(f"result:{result_id}")
        if cached:
            return cached
        return await self.db.get_result(result_id)
```

## Data Models

### 1. Input Models
```python
class OCRTask(BaseModel):
    """OCR processing task"""
    image_id: str
    priority: Optional[int] = 0
    callback_url: Optional[str]
    settings: OCRSettings

class OCRSettings(BaseModel):
    """OCR processing settings"""
    min_confidence: float = 0.8
    detect_regions: bool = True
    enhance_image: bool = True
    validate_results: bool = True
```

### 2. Result Models
```python
class OCRResult(BaseModel):
    """OCR processing result"""
    task_id: str
    status: ProcessingStatus
    companies: List[Company]
    booths: List[Booth]
    confidence: float
    processing_time: float
    errors: Optional[List[ProcessingError]]

class Company(BaseModel):
    """Extracted company information"""
    name: str
    booth_id: str
    confidence: float
    region: Region
```

## API Endpoints

### 1. Task Management
```python
@router.post("/tasks")
async def create_task(task: OCRTask) -> TaskResponse:
    """Create new OCR processing task"""
    task_id = await queue.enqueue(task)
    return TaskResponse(task_id=task_id)

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> TaskStatus:
    """Get task processing status"""
    return await queue.get_status(task_id)
```

### 2. Result Management
```python
@router.get("/results/{result_id}")
async def get_result(result_id: str) -> OCRResult:
    """Get OCR processing result"""
    return await result_manager.get_result(result_id)

@router.post("/results/{result_id}/validate")
async def validate_result(result_id: str, updates: ResultUpdates) -> OCRResult:
    """Update and validate OCR result"""
    return await result_manager.update_result(result_id, updates)
```

## Error Handling

### 1. Error Types
```python
class OCRError(Exception):
    """Base OCR processing error"""
    def __init__(self, message: str, details: dict):
        self.message = message
        self.details = details

class ImageProcessingError(OCRError):
    """Image processing/preparation error"""
    pass

class TextExtractionError(OCRError):
    """Text extraction error"""
    pass
```

### 2. Error Handling
```python
@app.exception_handler(OCRError)
async def handle_ocr_error(request: Request, error: OCRError) -> JSONResponse:
    """Handle OCR-related errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": error.message,
            "details": error.details,
            "type": error.__class__.__name__
        }
    )
```

## Configuration

### 1. Service Configuration
```python
class OCRServiceConfig(BaseSettings):
    """OCR service configuration"""
    tesseract_path: str
    min_confidence: float = 0.8
    max_retries: int = 3
    timeout: int = 300
    batch_size: int = 10
```

### 2. Infrastructure Configuration
```python
class InfraConfig(BaseSettings):
    """Infrastructure configuration"""
    redis_url: str
    db_url: str
    storage_path: str
    worker_count: int = 4
```

## Monitoring

### 1. Metrics
```python
class OCRMetrics:
    """OCR processing metrics"""
    
    async def record_processing_time(self, duration: float):
        """Record processing duration"""
        await prometheus.histogram(
            'ocr_processing_duration_seconds',
            duration
        )

    async def record_accuracy(self, confidence: float):
        """Record OCR confidence score"""
        await prometheus.gauge(
            'ocr_confidence_score',
            confidence
        )
```

### 2. Health Checks
```python
@router.get("/health")
async def health_check() -> HealthStatus:
    """Service health check"""
    return HealthStatus(
        status="healthy",
        components={
            "tesseract": await check_tesseract(),
            "database": await check_database(),
            "redis": await check_redis()
        }
    )
```

## Implementation Notes

1. **Performance Optimization**
   - Use async processing throughout
   - Implement caching at multiple levels
   - Optimize image preprocessing
   - Batch process when possible

2. **Reliability**
   - Implement retry mechanisms
   - Use circuit breakers
   - Handle partial failures
   - Maintain audit logs

3. **Scalability**
   - Stateless design
   - Horizontal scaling
   - Queue-based processing
   - Efficient resource usage

4. **Maintenance**
   - Comprehensive logging
   - Regular metric collection
   - Performance monitoring
   - Error tracking

## Next Steps

1. Set up project structure
2. Implement core OCR module
3. Add queue management
4. Create API endpoints
5. Add monitoring
6. Write tests