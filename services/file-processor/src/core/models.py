from pydantic import BaseModel
from typing import Optional, Dict, Any

class FileInfo(BaseModel):
    """Information about the processed file"""
    original_filename: str
    file_type: str
    file_size: int
    processed_path: str
    metadata: Optional[Dict[str, Any]] = None

class ProcessingResponse(BaseModel):
    """Response model for file processing endpoints"""
    status: str
    message: str
    file_info: Optional[FileInfo] = None