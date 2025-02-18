import os
import aiofiles
from fastapi import UploadFile
from PIL import Image
from PyPDF2 import PdfReader
from datetime import datetime
from .models import FileInfo
from utils.image_utils import preprocess_image

class FileProcessor:
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        self.processed_dir = os.path.join(os.getcwd(), "processed")
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    async def process_file(self, file: UploadFile) -> FileInfo:
        """
        Process uploaded file
        
        Args:
            file (UploadFile): The uploaded file
            
        Returns:
            FileInfo: Information about the processed file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{timestamp}{file_extension}"
        
        # Save original file
        upload_path = os.path.join(self.upload_dir, unique_filename)
        await self._save_file(file, upload_path)
        
        # Get content type from file extension
        content_type = self._get_content_type(file_extension)
        
        # Process based on content type
        if content_type == "application/pdf":
            raise NotImplementedError("PDF processing not yet implemented")
        else:
            processed_path = await self._process_image(upload_path)
        
        # Get file size
        file_size = os.path.getsize(upload_path)
        
        return FileInfo(
            original_filename=original_filename,
            file_type=content_type,
            file_size=file_size,
            processed_path=processed_path,
            metadata={
                "upload_path": upload_path,
                "timestamp": timestamp
            }
        )

    def _get_content_type(self, extension: str) -> str:
        """Map file extension to content type"""
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        return content_types.get(extension, '')

    async def _save_file(self, file: UploadFile, path: str):
        """Save uploaded file to disk"""
        async with aiofiles.open(path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

    async def _process_image(self, image_path: str) -> str:
        """
        Process image file
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Path to processed image
        """
        # Open and preprocess image
        with Image.open(image_path) as img:
            processed_img = preprocess_image(img)
            
            # Save processed image
            filename = os.path.basename(image_path)
            processed_path = os.path.join(self.processed_dir, f"processed_{filename}")
            processed_img.save(processed_path)
            
            return processed_path