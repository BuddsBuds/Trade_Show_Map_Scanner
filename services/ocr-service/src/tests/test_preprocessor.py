import pytest
import numpy as np
from PIL import Image
import cv2
from unittest.mock import patch

from ..core.preprocessor import ImagePreprocessor, Region
from ..core.errors import ImageProcessingError

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    # Create a 200x100 white image with black text
    img = Image.new('RGB', (200, 100), color='white')
    return img

@pytest.fixture
def skewed_image():
    """Create a skewed image for testing deskewing"""
    # Create a white image
    img = np.ones((100, 200), dtype=np.uint8) * 255
    
    # Add a rotated rectangle
    center = (100, 50)
    size = (160, 60)
    angle = 15  # 15 degrees rotation
    
    rect = ((center[0], center[1]), size, angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    
    # Draw the rotated rectangle
    cv2.drawContours(img, [box], 0, (0, 0, 0), 2)
    
    return Image.fromarray(img)

@pytest.fixture
def noisy_image():
    """Create a noisy image for testing noise removal"""
    # Create base image
    img = np.ones((100, 200), dtype=np.uint8) * 255
    
    # Add random noise
    noise = np.random.normal(0, 25, img.shape)
    img = img + noise
    img = np.clip(img, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img)

@pytest.mark.asyncio
async def test_image_preprocessor_initialization():
    """Test ImagePreprocessor initialization"""
    preprocessor = ImagePreprocessor()
    assert preprocessor.min_region_size == 50
    assert preprocessor.min_region_confidence > 0

@pytest.mark.asyncio
async def test_prepare_pipeline(sample_image):
    """Test complete preprocessing pipeline"""
    preprocessor = ImagePreprocessor()
    
    # Process image
    processed = await preprocessor.prepare(sample_image)
    
    # Verify output
    assert isinstance(processed, Image.Image)
    assert processed.size == sample_image.size
    assert processed.mode in ['L', 'RGB']  # Either grayscale or RGB

@pytest.mark.asyncio
async def test_normalize_image(sample_image):
    """Test image normalization"""
    preprocessor = ImagePreprocessor()
    
    # Convert to OpenCV format
    cv_image = np.array(sample_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    
    # Normalize
    normalized = await preprocessor._normalize(cv_image)
    
    # Verify output
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == cv_image.shape
    assert normalized.dtype == np.uint8
    
    # Check if histogram is more balanced
    hist_orig = cv2.calcHist([cv_image], [0], None, [256], [0, 256])
    hist_norm = cv2.calcHist([normalized], [0], None, [256], [0, 256])
    
    # Verify histogram spread
    assert np.std(hist_norm) <= np.std(hist_orig)

@pytest.mark.asyncio
async def test_enhance_contrast(sample_image):
    """Test contrast enhancement"""
    preprocessor = ImagePreprocessor()
    
    # Convert to OpenCV format
    cv_image = np.array(sample_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    
    # Enhance contrast
    enhanced = await preprocessor._enhance_contrast(cv_image)
    
    # Verify output
    assert isinstance(enhanced, np.ndarray)
    assert enhanced.shape == cv_image.shape
    assert enhanced.dtype == np.uint8
    
    # Check if contrast is increased
    std_orig = np.std(cv_image)
    std_enhanced = np.std(enhanced)
    assert std_enhanced >= std_orig

@pytest.mark.asyncio
async def test_remove_noise(noisy_image):
    """Test noise removal"""
    preprocessor = ImagePreprocessor()
    
    # Convert to OpenCV format
    cv_image = np.array(noisy_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    
    # Remove noise
    denoised = await preprocessor._remove_noise(cv_image)
    
    # Verify output
    assert isinstance(denoised, np.ndarray)
    assert denoised.shape == cv_image.shape
    
    # Check if noise is reduced
    noise_level_orig = np.std(cv_image)
    noise_level_denoised = np.std(denoised)
    assert noise_level_denoised < noise_level_orig

@pytest.mark.asyncio
async def test_deskew(skewed_image):
    """Test image deskewing"""
    preprocessor = ImagePreprocessor()
    
    # Convert to OpenCV format
    cv_image = np.array(skewed_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    
    # Deskew
    deskewed = await preprocessor._deskew(cv_image)
    
    # Verify output
    assert isinstance(deskewed, np.ndarray)
    assert deskewed.shape == cv_image.shape
    
    # Check if angle is corrected
    # This is a basic check - in real scenarios, you might want to use
    # more sophisticated methods to verify deskewing
    orig_angle = _calculate_skew_angle(cv_image)
    new_angle = _calculate_skew_angle(deskewed)
    assert abs(new_angle) < abs(orig_angle)

@pytest.mark.asyncio
async def test_detect_regions(sample_image):
    """Test region detection"""
    preprocessor = ImagePreprocessor()
    
    # Convert to OpenCV format
    cv_image = np.array(sample_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    
    # Detect regions
    regions = await preprocessor._detect_regions(cv_image)
    
    # Verify output
    assert isinstance(regions, list)
    for region in regions:
        assert isinstance(region, Region)
        assert len(region.bbox) == 4
        assert 0 <= region.confidence <= 1
        
        # Verify region size
        width = region.bbox[2]
        height = region.bbox[3]
        assert width >= preprocessor.min_region_size
        assert height >= preprocessor.min_region_size

@pytest.mark.asyncio
async def test_error_handling(sample_image):
    """Test error handling in preprocessing"""
    preprocessor = ImagePreprocessor()
    
    # Test with invalid image
    with pytest.raises(ImageProcessingError):
        await preprocessor.prepare(None)
    
    # Test with corrupted image data
    corrupted_image = np.ones((100, 200), dtype=np.uint8)
    corrupted_image[50, 100] = 256  # Invalid pixel value
    with pytest.raises(ImageProcessingError):
        await preprocessor.prepare(Image.fromarray(corrupted_image))

def _calculate_skew_angle(image):
    """Helper function to calculate skew angle"""
    coords = np.column_stack(np.where(image < 127))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    return angle