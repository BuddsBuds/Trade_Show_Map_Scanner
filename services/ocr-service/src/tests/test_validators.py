import os
import pytest
from pathlib import Path
from PIL import Image

from ..utils.validators import (
    validate_file_size,
    validate_file_extension,
    validate_image,
    validate_confidence,
    ensure_directory,
    sanitize_filename,
    generate_safe_path
)
from ..core.errors import ValidationError, StorageError

@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image file for testing"""
    image_path = tmp_path / "test_image.jpg"
    # Create a 100x100 black image
    image = Image.new('RGB', (100, 100), color='black')
    image.save(image_path)
    return image_path

@pytest.fixture
def large_file(tmp_path):
    """Create a large test file"""
    file_path = tmp_path / "large_file.txt"
    # Create a 2MB file
    with open(file_path, 'wb') as f:
        f.write(b'0' * (2 * 1024 * 1024))
    return file_path

def test_validate_file_size(large_file):
    """Test file size validation"""
    # Test valid file size
    assert validate_file_size(large_file, max_size=3 * 1024 * 1024)  # 3MB limit
    
    # Test file size exceeding limit
    with pytest.raises(StorageError) as exc_info:
        validate_file_size(large_file, max_size=1 * 1024 * 1024)  # 1MB limit
    assert "exceeds maximum allowed size" in str(exc_info.value)
    
    # Test non-existent file
    with pytest.raises(StorageError) as exc_info:
        validate_file_size("nonexistent.txt", max_size=1024)
    assert "Error checking file size" in str(exc_info.value)

def test_validate_file_extension(sample_image, tmp_path):
    """Test file extension validation"""
    # Test valid extension
    assert validate_file_extension(sample_image, [".jpg", ".jpeg", ".png"])
    
    # Test invalid extension
    invalid_file = tmp_path / "test.txt"
    invalid_file.touch()
    with pytest.raises(ValidationError) as exc_info:
        validate_file_extension(invalid_file, [".jpg", ".jpeg", ".png"])
    assert "not allowed" in str(exc_info.value)
    
    # Test case insensitive validation
    assert validate_file_extension(sample_image, [".JPG", ".JPEG", ".PNG"])

def test_validate_image(sample_image):
    """Test image validation"""
    # Test valid image
    assert validate_image(sample_image)
    
    # Test minimum dimensions
    assert validate_image(sample_image, min_width=50, min_height=50)
    
    # Test image too small
    with pytest.raises(ValidationError) as exc_info:
        validate_image(sample_image, min_width=200, min_height=200)
    assert "less than minimum required" in str(exc_info.value)
    
    # Test invalid image file
    invalid_image = sample_image.parent / "invalid.jpg"
    invalid_image.write_text("not an image")
    with pytest.raises(ValidationError) as exc_info:
        validate_image(invalid_image)
    assert "Error validating image" in str(exc_info.value)

def test_validate_confidence():
    """Test confidence score validation"""
    # Test valid confidence
    assert validate_confidence(0.85, min_confidence=0.8)
    
    # Test confidence too low
    with pytest.raises(ValidationError) as exc_info:
        validate_confidence(0.7, min_confidence=0.8)
    assert "below minimum required" in str(exc_info.value)
    
    # Test with context
    with pytest.raises(ValidationError) as exc_info:
        validate_confidence(0.7, min_confidence=0.8, context="company name extraction")
    assert "company name extraction" in str(exc_info.value)

def test_ensure_directory(tmp_path):
    """Test directory creation"""
    # Test creating new directory
    new_dir = tmp_path / "test_dir" / "nested"
    created_dir = ensure_directory(new_dir)
    assert created_dir.exists()
    assert created_dir.is_dir()
    
    # Test existing directory
    assert ensure_directory(new_dir) == created_dir
    
    # Test invalid path (on systems where /dev/null/invalid would be invalid)
    with pytest.raises(StorageError) as exc_info:
        ensure_directory("/dev/null/invalid")
    assert "Error creating directory" in str(exc_info.value)

def test_sanitize_filename():
    """Test filename sanitization"""
    # Test basic sanitization
    assert sanitize_filename("test.jpg") == "test.jpg"
    
    # Test path traversal
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    
    # Test unsafe characters
    assert sanitize_filename('test<>:"/\\|?*.jpg') == "test_________.jpg"
    
    # Test empty filename
    assert sanitize_filename("") == "unnamed_file"
    
    # Test null bytes
    assert sanitize_filename("test\0.jpg") == "test_.jpg"

def test_generate_safe_path(tmp_path):
    """Test safe path generation"""
    # Test basic path generation
    safe_path = generate_safe_path(tmp_path, "test.jpg")
    assert safe_path.parent == tmp_path
    assert safe_path.name == "test.jpg"
    
    # Test path with unsafe characters
    safe_path = generate_safe_path(tmp_path, 'test<>:"/\\|?*.jpg')
    assert safe_path.name == "test_________.jpg"
    
    # Test long filename
    long_name = "a" * 300 + ".jpg"
    safe_path = generate_safe_path(tmp_path, long_name, max_length=255)
    assert len(str(safe_path)) <= 255
    assert safe_path.suffix == ".jpg"
    
    # Test creating in non-existent directory
    new_dir = tmp_path / "new_dir"
    safe_path = generate_safe_path(new_dir, "test.jpg")
    assert safe_path.parent.exists()
    assert safe_path.parent == new_dir