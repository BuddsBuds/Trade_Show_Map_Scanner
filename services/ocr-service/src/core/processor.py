from typing import List, Optional
from PIL import Image
import pytesseract
from datetime import datetime

from ..config.settings import OCRConfig
from .errors import TextExtractionError, ValidationError, ImageProcessingError
from ..utils.validators import validate_confidence
from .preprocessor import ImagePreprocessor
from .analyzer import TextAnalyzer, AnalysisResult

class TesseractWrapper:
    """Wrapper for Tesseract OCR engine"""
    
    def __init__(self, config: OCRConfig):
        self.config = config
        pytesseract.pytesseract.tesseract_cmd = str(config.tesseract_path)
        
    async def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from image using Tesseract
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Extracted text
            
        Raises:
            TextExtractionError: If text extraction fails
        """
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.config.language,
                config='--psm 11'  # Sparse text with OSD
            )
            
            if not text.strip():
                raise TextExtractionError(
                    message="No text extracted from image",
                    confidence=0.0
                )
                
            # Get confidence scores
            data = pytesseract.image_to_data(
                image,
                lang=self.config.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [float(conf) / 100.0 for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Validate confidence
            validate_confidence(
                avg_confidence,
                self.config.min_confidence,
                "text extraction"
            )
            
            return text
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise TextExtractionError(
                    message="Low confidence in extracted text",
                    confidence=avg_confidence,
                    details={"original_error": str(e)}
                )
            raise TextExtractionError(
                message=f"Failed to extract text: {str(e)}",
                confidence=0.0,
                details={"original_error": str(e)}
            )

class OCRProcessor:
    """Core OCR processing engine"""
    
    def __init__(self, config: OCRConfig):
        self.config = config
        self.tesseract = TesseractWrapper(config)
        self.preprocessor = ImagePreprocessor()
        self.analyzer = TextAnalyzer()
        
    async def process_image(self, image: Image.Image) -> AnalysisResult:
        """
        Main processing pipeline
        
        Args:
            image: PIL Image object
            
        Returns:
            AnalysisResult: Processing result containing extracted information
            
        Raises:
            OCRError: If processing fails at any stage
        """
        start_time = datetime.utcnow()
        
        try:
            # Preprocess image
            processed_image = await self.preprocessor.prepare(image)
            
            # Extract text
            text = await self.tesseract.extract_text(processed_image)
            
            # Analyze text and extract information
            result = await self.analyzer.analyze(text)
            
            # Update processing time
            result.processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            if isinstance(e, (TextExtractionError, ImageProcessingError, ValidationError)):
                if hasattr(e, 'details'):
                    e.details["processing_time"] = processing_time
                raise
                
            raise TextExtractionError(
                message=f"OCR processing failed: {str(e)}",
                confidence=0.0,
                details={
                    "processing_time": processing_time,
                    "original_error": str(e)
                }
            )