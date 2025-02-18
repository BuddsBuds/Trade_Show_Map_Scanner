"""
Test configuration and fixtures for the OCR service.
"""
import os
import pytest
import yaml
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Store original environment
    original_env = os.environ.get("ENVIRONMENT")
    
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    
    yield
    
    # Restore original environment
    if original_env:
        os.environ["ENVIRONMENT"] = original_env
    else:
        del os.environ["ENVIRONMENT"]

@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    config_path = Path("config/testing/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Test configuration not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_data_dir():
    """Create and return test data directory."""
    data_dir = Path("data/test")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    yield data_dir
    
    # Clean up the entire test data directory after all tests
    if data_dir.exists():
        shutil.rmtree(data_dir)

@pytest.fixture(scope="function")
def upload_dir(test_data_dir):
    """Create and return upload directory for tests."""
    upload_dir = test_data_dir / "uploads"
    upload_dir.mkdir(exist_ok=True)
    
    # Create a test file to ensure cleanup works
    test_file = upload_dir / "test.txt"
    test_file.write_text("test content")
    
    yield upload_dir
    
    # Clean up test files
    for file in upload_dir.glob("*"):
        if file.is_file():
            file.unlink()

@pytest.fixture(scope="function")
def processed_dir(test_data_dir):
    """Create and return processed directory for tests."""
    processed_dir = test_data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # Create a test file to ensure cleanup works
    test_file = processed_dir / "test.txt"
    test_file.write_text("test content")
    
    yield processed_dir
    
    # Clean up test files
    for file in processed_dir.glob("*"):
        if file.is_file():
            file.unlink()

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    from src.main import create_app
    app = create_app()
    with TestClient(app) as client:
        yield client