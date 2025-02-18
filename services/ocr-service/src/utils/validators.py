import os
from pathlib import Path
from typing import List, Optional, Union
from PIL import Image

from ..core.errors import ValidationError, StorageError

def validate_file_size(file_path: Union[str, Path], max_size: int) -> bool:
    """
    Validate file size against maximum allowed size
    
    Args:
        file_path: Path to the file
        max_size: Maximum allowed size in bytes
        
    Returns:
        bool: True if file size is valid
        
    Raises:
        StorageError: If file size exceeds maximum allowed size
    """
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise StorageError(
                message=f"File size {file_size} exceeds maximum allowed size {max_size}",
                file_path=str(file_path),
                operation="size_validation"
            )
        return True
    except OSError as e:
        raise StorageError(
            message=f"Error checking file size: {str(e)}",
            file_path=str(file_path),
            operation="size_validation"
        )

def validate_file_extension(
    file_path: Union[str, Path],
    allowed_extensions: List[str]
) -> bool:
    """
    Validate file extension against list of allowed extensions
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed file extensions
        
    Returns:
        bool: True if file extension is valid
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    ext = os.path.splitext(str(file_path))[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            message=f"File extension {ext} not allowed. Allowed extensions: {allowed_extensions}",
            validation_errors={"extension": ext, "allowed": allowed_extensions}
        )
    return True

def validate_image(
    image_path: Union[str, Path],
    min_width: Optional[int] = None,
    min_height: Optional[int] = None
) -> bool:
    """
    Validate image file
    
    Args:
        image_path: Path to the image file
        min_width: Minimum required width in pixels
        min_height: Minimum required height in pixels
        
    Returns:
        bool: True if image is valid
        
    Raises:
        ValidationError: If image validation fails
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            if min_width and width < min_width:
                raise ValidationError(
                    message=f"Image width {width}px is less than minimum required {min_width}px",
                    validation_errors={"width": width, "min_width": min_width}
                )
                
            if min_height and height < min_height:
                raise ValidationError(
                    message=f"Image height {height}px is less than minimum required {min_height}px",
                    validation_errors={"height": height, "min_height": min_height}
                )
                
            return True
    except (IOError, OSError) as e:
        raise ValidationError(
            message=f"Error validating image: {str(e)}",
            validation_errors={"error": str(e)}
        )

def validate_confidence(
    confidence: float,
    min_confidence: float,
    context: Optional[str] = None
) -> bool:
    """
    Validate OCR confidence score
    
    Args:
        confidence: Confidence score to validate
        min_confidence: Minimum required confidence score
        context: Optional context for error message
        
    Returns:
        bool: True if confidence is valid
        
    Raises:
        ValidationError: If confidence is below minimum required
    """
    if confidence < min_confidence:
        raise ValidationError(
            message=f"Confidence score {confidence} is below minimum required {min_confidence}"
            + (f" for {context}" if context else ""),
            validation_errors={
                "confidence": confidence,
                "min_confidence": min_confidence,
                "context": context
            }
        )
    return True

def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
        
    Returns:
        Path: Path object for the directory
        
    Raises:
        StorageError: If directory cannot be created
    """
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise StorageError(
            message=f"Error creating directory: {str(e)}",
            file_path=str(directory),
            operation="create_directory"
        )

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and ensure safe characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove path separators and null bytes
    filename = os.path.basename(filename)
    
    # Replace potentially dangerous characters
    unsafe_chars = '<>:"/\\|?*\0'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
        
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
        
    return filename

def generate_safe_path(
    base_dir: Union[str, Path],
    filename: str,
    max_length: int = 255
) -> Path:
    """
    Generate safe file path from base directory and filename
    
    Args:
        base_dir: Base directory path
        filename: Original filename
        max_length: Maximum path length
        
    Returns:
        Path: Safe file path
        
    Raises:
        StorageError: If safe path cannot be generated
    """
    try:
        # Ensure base directory exists
        base_path = ensure_directory(base_dir)
        
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # Generate full path
        full_path = base_path / safe_filename
        
        # Handle path length restrictions
        if len(str(full_path)) > max_length:
            name, ext = os.path.splitext(safe_filename)
            # Truncate name while preserving extension
            max_name_length = max_length - len(str(base_path)) - len(ext) - 1
            truncated_name = name[:max_name_length]
            full_path = base_path / f"{truncated_name}{ext}"
            
        return full_path
    except Exception as e:
        raise StorageError(
            message=f"Error generating safe path: {str(e)}",
            file_path=str(filename),
            operation="generate_safe_path"
        )