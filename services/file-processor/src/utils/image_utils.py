from PIL import Image, ImageEnhance, ImageOps

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR results
    
    Args:
        image (Image.Image): Original PIL Image
        
    Returns:
        Image.Image: Preprocessed image
    """
    try:
        # Convert to grayscale
        img = image.convert('L')
        
        # Auto-rotate based on EXIF data
        img = ImageOps.exif_transpose(img)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)  # Increase contrast
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        # Resize if too large (maintain aspect ratio)
        max_dimension = 2000
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        # Log the error and re-raise with more context
        raise Exception(f"Error preprocessing image: {str(e)}") from e