from typing import Any, Dict, Optional
from datetime import datetime

class OCRError(Exception):
    """Base exception class for OCR service errors"""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code or self.__class__.__name__
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "type": self.__class__.__name__
        }

class ConfigurationError(OCRError):
    """Error raised when there's an issue with service configuration"""
    pass

class ImageProcessingError(OCRError):
    """Error raised during image preprocessing"""
    def __init__(
        self,
        message: str,
        image_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "image_id": image_id,
            "operation": operation,
            **kwargs
        }
        super().__init__(message, details, "IMAGE_PROCESSING_ERROR")

class TextExtractionError(OCRError):
    """Error raised during text extraction from image"""
    def __init__(
        self,
        message: str,
        image_id: Optional[str] = None,
        confidence: Optional[float] = None,
        **kwargs
    ):
        details = {
            "image_id": image_id,
            "confidence": confidence,
            **kwargs
        }
        super().__init__(message, details, "TEXT_EXTRACTION_ERROR")

class ValidationError(OCRError):
    """Error raised during result validation"""
    def __init__(
        self,
        message: str,
        result_id: Optional[str] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = {
            "result_id": result_id,
            "validation_errors": validation_errors,
            **kwargs
        }
        super().__init__(message, details, "VALIDATION_ERROR")

class QueueError(OCRError):
    """Error raised during queue operations"""
    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "task_id": task_id,
            "operation": operation,
            **kwargs
        }
        super().__init__(message, details, "QUEUE_ERROR")

class StorageError(OCRError):
    """Error raised during storage operations"""
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "file_path": file_path,
            "operation": operation,
            **kwargs
        }
        super().__init__(message, details, "STORAGE_ERROR")

class DatabaseError(OCRError):
    """Error raised during database operations"""
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = {
            "operation": operation,
            "table": table,
            **kwargs
        }
        super().__init__(message, details, "DATABASE_ERROR")

class TesseractError(OCRError):
    """Error raised during Tesseract OCR operations"""
    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        exit_code: Optional[int] = None,
        **kwargs
    ):
        details = {
            "command": command,
            "exit_code": exit_code,
            **kwargs
        }
        super().__init__(message, details, "TESSERACT_ERROR")

class ServiceError(OCRError):
    """Error raised for general service issues"""
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "service": service,
            "operation": operation,
            **kwargs
        }
        super().__init__(message, details, "SERVICE_ERROR")