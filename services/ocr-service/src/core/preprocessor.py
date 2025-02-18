from typing import List, Tuple, Optional
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from dataclasses import dataclass

from .errors import ImageProcessingError

@dataclass
class Region:
    """Represents a detected region in the image"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float

class ImagePreprocessor:
    """Image preprocessing for optimal OCR"""
    
    def __init__(self):
        self.min_region_size = 50  # Minimum region size in pixels
        self.min_region_confidence = 0.6  # Minimum confidence for region detection
    
    async def prepare(self, image: Image.Image) -> Image.Image:
        """
        Prepare image for OCR processing
        
        Args:
            image: PIL Image object
            
        Returns:
            Image.Image: Processed image ready for OCR
            
        Raises:
            ImageProcessingError: If processing fails
        """
        try:
            # Convert PIL Image to OpenCV format for processing
            cv_image = self._pil_to_cv2(image)
            
            # Apply preprocessing pipeline
            processed = await self._pipeline(cv_image)
            
            # Convert back to PIL Image
            return self._cv2_to_pil(processed)
            
        except Exception as e:
            raise ImageProcessingError(
                message=f"Image preprocessing failed: {str(e)}",
                operation="prepare"
            )
    
    async def _pipeline(self, image: np.ndarray) -> np.ndarray:
        """Apply preprocessing pipeline"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            # Apply preprocessing steps
            normalized = await self._normalize(gray)
            enhanced = await self._enhance_contrast(normalized)
            denoised = await self._remove_noise(enhanced)
            deskewed = await self._deskew(denoised)
            
            return deskewed
            
        except Exception as e:
            raise ImageProcessingError(
                message=f"Preprocessing pipeline failed: {str(e)}",
                operation="pipeline"
            )
    
    async def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image"""
        try:
            # Apply adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            return clahe.apply(image)
        except Exception as e:
            raise ImageProcessingError(
                message=f"Image normalization failed: {str(e)}",
                operation="normalize"
            )
    
    async def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast"""
        try:
            # Convert to PIL Image for contrast enhancement
            pil_image = self._cv2_to_pil(image)
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(1.5)  # Increase contrast by 50%
            return self._pil_to_cv2(enhanced)
        except Exception as e:
            raise ImageProcessingError(
                message=f"Contrast enhancement failed: {str(e)}",
                operation="enhance_contrast"
            )
    
    async def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        try:
            # Apply bilateral filter to remove noise while preserving edges
            return cv2.bilateralFilter(image, 9, 75, 75)
        except Exception as e:
            raise ImageProcessingError(
                message=f"Noise removal failed: {str(e)}",
                operation="remove_noise"
            )
    
    async def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Deskew image"""
        try:
            # Find all contours
            contours, _ = cv2.findContours(
                image, 
                cv2.RETR_LIST, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Find the largest contour
            if not contours:
                return image
                
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Find minimum area rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[-1]
            
            # Determine if we need to add 90 degrees
            if angle < -45:
                angle = 90 + angle
                
            # Get image center and rotation matrix
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Perform rotation
            return cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
        except Exception as e:
            raise ImageProcessingError(
                message=f"Image deskewing failed: {str(e)}",
                operation="deskew"
            )
    
    async def _detect_regions(self, image: np.ndarray) -> List[Region]:
        """
        Detect booth regions in floor plan
        
        Args:
            image: OpenCV image array
            
        Returns:
            List[Region]: List of detected regions with confidence scores
        """
        try:
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                image,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                11,
                2
            )
            
            # Find contours
            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            regions = []
            for contour in contours:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter small regions
                if w < self.min_region_size or h < self.min_region_size:
                    continue
                
                # Calculate region confidence based on area and aspect ratio
                area = w * h
                aspect_ratio = min(w, h) / max(w, h)
                confidence = min(
                    1.0,
                    (area / (image.shape[0] * image.shape[1])) * aspect_ratio * 2
                )
                
                if confidence >= self.min_region_confidence:
                    regions.append(Region((x, y, w, h), confidence))
            
            return regions
            
        except Exception as e:
            raise ImageProcessingError(
                message=f"Region detection failed: {str(e)}",
                operation="detect_regions"
            )
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        return np.array(pil_image)
    
    def _cv2_to_pil(self, cv_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL format"""
        return Image.fromarray(cv_image)