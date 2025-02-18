"""
Tests for test fixtures to ensure proper setup and cleanup.
"""
import os
from pathlib import Path

def test_test_data_dir_creation(test_data_dir):
    """Test that test_data_dir fixture creates directory."""
    assert test_data_dir.exists()
    assert test_data_dir.is_dir()
    assert test_data_dir == Path("data/test")

def test_upload_dir_creation_and_cleanup(upload_dir):
    """Test upload_dir fixture creates directory and test file."""
    # Check directory creation
    assert upload_dir.exists()
    assert upload_dir.is_dir()
    
    # Check test file creation
    test_file = upload_dir / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "test content"
    
    # Create additional test file
    another_file = upload_dir / "another.txt"
    another_file.write_text("more content")
    
    # Files should exist now
    assert test_file.exists()
    assert another_file.exists()

def test_processed_dir_creation_and_cleanup(processed_dir):
    """Test processed_dir fixture creates directory and test file."""
    # Check directory creation
    assert processed_dir.exists()
    assert processed_dir.is_dir()
    
    # Check test file creation
    test_file = processed_dir / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "test content"
    
    # Create additional test file
    another_file = processed_dir / "another.txt"
    another_file.write_text("more content")
    
    # Files should exist now
    assert test_file.exists()
    assert another_file.exists()

def test_environment_setup(setup_test_environment):
    """Test environment setup and cleanup."""
    assert os.environ.get("ENVIRONMENT") == "testing"
    
    # Set a different value to test cleanup
    os.environ["ENVIRONMENT"] = "modified"
    
def test_environment_cleanup(setup_test_environment):
    """Test that environment is properly cleaned up between tests."""
    assert os.environ.get("ENVIRONMENT") == "testing"

def test_test_config_loading(test_config):
    """Test that test configuration is properly loaded."""
    assert test_config is not None
    assert "service" in test_config
    assert test_config["service"]["environment"] == "testing"
    assert test_config["service"]["port"] == 8001

def test_test_client_creation(test_client):
    """Test that test client is properly created."""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["environment"] == "testing"