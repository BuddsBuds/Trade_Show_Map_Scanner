import pytest
from PIL import Image
import numpy as np
from unittest.mock import Mock, patch

from ..core.processor import OCRProcessor, TesseractWrapper
from ..core.errors import TextExtractionError
from ..config.settings import OCRConfig

@pytest.fixture
def mock_config():
    """Create mock OCR configuration"""
    return OCRConfig(
        tesseract_path="/usr/local/bin/tesseract",
        min_confidence=0.8,
        max_retries=3,
        timeout=300,
        batch_size=10,
        language="eng"
    )

@pytest.fixture
def sample_image():
    """Create a sample image with text"""
    # Create a white image
    img = Image.new('RGB', (200, 100), color='white')
    return img

@pytest.fixture
def mock_tesseract_data():
    """Mock Tesseract OCR output data"""
    return {
        'text': ['Company: Test Corp', 'Booth: A123'],
        'conf': ['90', '85'],
        'level': [1, 1],
        'page_num': [1, 1],
        'block_num': [1, 1],
        'par_num': [1, 1],
        'line_num': [1, 2],
        'word_num': [1, 1]
    }

@pytest.mark.asyncio
async def test_tesseract_wrapper_extract_text(mock_config, sample_image, mock_tesseract_data):
    """Test text extraction using TesseractWrapper"""
    wrapper = TesseractWrapper(mock_config)
    
    with patch('pytesseract.image_to_string') as mock_to_string, \
         patch('pytesseract.image_to_data') as mock_to_data:
        
        # Mock Tesseract outputs
        mock_to_string.return_value = "Company: Test Corp\nBooth: A123"
        mock_to_data.return_value = mock_tesseract_data
        
        # Test successful extraction
        text = await wrapper.extract_text(sample_image)
        assert "Company: Test Corp" in text
        assert "Booth: A123" in text
        
        # Verify Tesseract was called with correct parameters
        mock_to_string.assert_called_once_with(
            sample_image,
            lang="eng",
            config='--psm 11'
        )

@pytest.mark.asyncio
async def test_tesseract_wrapper_low_confidence(mock_config, sample_image):
    """Test handling of low confidence text extraction"""
    wrapper = TesseractWrapper(mock_config)
    
    with patch('pytesseract.image_to_string') as mock_to_string, \
         patch('pytesseract.image_to_data') as mock_to_data:
        
        # Mock low confidence output
        mock_to_string.return_value = "Unclear text"
        mock_to_data.return_value = {
            'text': ['Unclear text'],
            'conf': ['50'],  # Low confidence
            'level': [1],
            'page_num': [1],
            'block_num': [1],
            'par_num': [1],
            'line_num': [1],
            'word_num': [1]
        }
        
        # Test low confidence handling
        with pytest.raises(TextExtractionError) as exc_info:
            await wrapper.extract_text(sample_image)
        
        assert "Low confidence in extracted text" in str(exc_info.value)

@pytest.mark.asyncio
async def test_tesseract_wrapper_no_text(mock_config, sample_image):
    """Test handling of empty text extraction"""
    wrapper = TesseractWrapper(mock_config)
    
    with patch('pytesseract.image_to_string') as mock_to_string:
        # Mock empty output
        mock_to_string.return_value = ""
        
        # Test empty text handling
        with pytest.raises(TextExtractionError) as exc_info:
            await wrapper.extract_text(sample_image)
        
        assert "No text extracted from image" in str(exc_info.value)

@pytest.mark.asyncio
async def test_ocr_processor_process_image(mock_config, sample_image, mock_tesseract_data):
    """Test complete OCR processing pipeline"""
    processor = OCRProcessor(mock_config)
    
    # Mock component outputs
    with patch('pytesseract.image_to_string') as mock_to_string, \
         patch('pytesseract.image_to_data') as mock_to_data:
        
        mock_to_string.return_value = "Company: Test Corp\nBooth: A123"
        mock_to_data.return_value = mock_tesseract_data
        
        # Process image
        result = await processor.process_image(sample_image)
        
        # Verify result structure
        assert hasattr(result, 'companies')
        assert hasattr(result, 'booths')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'processing_time')
        
        # Verify processing time is reasonable
        assert result.processing_time > 0
        assert result.processing_time < 10  # Should process within 10 seconds

@pytest.mark.asyncio
async def test_ocr_processor_error_handling(mock_config, sample_image):
    """Test error handling in OCR processing pipeline"""
    processor = OCRProcessor(mock_config)
    
    with patch('pytesseract.image_to_string') as mock_to_string:
        # Simulate Tesseract error
        mock_to_string.side_effect = Exception("Tesseract error")
        
        # Test error handling
        with pytest.raises(TextExtractionError) as exc_info:
            await processor.process_image(sample_image)
        
        assert "OCR processing failed" in str(exc_info.value)
        assert "processing_time" in exc_info.value.details