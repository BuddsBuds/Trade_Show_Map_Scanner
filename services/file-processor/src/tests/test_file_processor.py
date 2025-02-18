import pytest
import os
from fastapi.testclient import TestClient
from fastapi import UploadFile
from PIL import Image
from io import BytesIO
from ..api.app import app
from ..core.file_processor import FileProcessor
from ..core.models import FileInfo
from ..utils.image_utils import preprocess_image

client = TestClient(app)

@pytest.fixture
def test_image():
    """Create a test image file"""
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

@pytest.fixture
def test_upload_file(test_image):
    """Create a FastAPI UploadFile object"""
    return UploadFile(filename="test.png", file=test_image)

@pytest.fixture
def file_processor():
    """Create a FileProcessor instance"""
    processor = FileProcessor()
    # Clean up test directories after tests
    yield processor
    for dir_path in [processor.upload_dir, processor.processed_dir]:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))
            os.rmdir(dir_path)

class TestFileProcessor:
    """Test file processing functionality"""

    def test_upload_valid_image(self, test_image):
        """Test uploading a valid image file"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.png", test_image, "image/png")}
        )
        assert response.status_code == 202
        assert response.json()["status"] == "success"
        assert "file_info" in response.json()
        
        file_info = response.json()["file_info"]
        assert file_info["original_filename"] == "test.png"
        assert file_info["file_type"] == "image/png"
        assert os.path.exists(file_info["processed_path"])

    def test_upload_invalid_file_type(self):
        """Test uploading an invalid file type"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", b"test content", "text/plain")}
        )
        assert response.status_code == 415
        assert "PDF, JPG, or PNG" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_process_image_file(self, file_processor, test_upload_file):
        """Test processing an image file"""
        result = await file_processor.process_file(test_upload_file)
        
        assert isinstance(result, FileInfo)
        assert result.original_filename == "test.png"
        assert result.file_type == "image/png"
        assert os.path.exists(result.processed_path)
        assert result.file_size > 0

    def test_create_upload_directories(self, file_processor):
        """Test creation of upload and processed directories"""
        assert os.path.exists(file_processor.upload_dir)
        assert os.path.exists(file_processor.processed_dir)

    @pytest.mark.asyncio
    async def test_pdf_processing_not_implemented(self, file_processor):
        """Test PDF processing raises NotImplementedError"""
        test_pdf = BytesIO(b"%PDF-1.5")  # Minimal PDF content
        upload_file = UploadFile(filename="test.pdf", file=test_pdf)
        
        with pytest.raises(NotImplementedError):
            await file_processor.process_file(upload_file)

    def test_image_preprocessing(self, file_processor):
        """Test image preprocessing functionality"""
        # Create large test image
        large_img = Image.new('RGB', (3000, 3000), color='white')
        img_byte_arr = BytesIO()
        large_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Create upload file
        upload_file = UploadFile(filename="large.png", file=img_byte_arr)
        
        # Process directly first to verify image processing works
        processed_img = preprocess_image(large_img)
        assert max(processed_img.size) <= 2000
        
        # Now test through the API
        response = client.post(
            "/api/v1/upload",
            files={"file": ("large.png", img_byte_arr, "image/png")}
        )
        
        if response.status_code != 202:
            print(f"Error response: {response.json()}")
            
        assert response.status_code == 202
        file_info = response.json()["file_info"]
        processed_path = file_info["processed_path"]
        
        # Verify the processed image
        with Image.open(processed_path) as processed_img:
            assert max(processed_img.size) <= 2000