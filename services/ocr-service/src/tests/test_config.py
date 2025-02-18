import pytest
from pathlib import Path
from pydantic import ValidationError

from ..config.settings import (
    Settings,
    OCRConfig,
    StorageConfig,
    QueueConfig
)

def test_ocr_config_validation():
    """Test OCR configuration validation"""
    # Test valid configuration
    valid_config = OCRConfig(
        tesseract_path="/usr/local/bin/tesseract",
        min_confidence=0.8,
        max_retries=3,
        timeout=300,
        batch_size=10,
        language="eng"
    )
    assert valid_config.min_confidence == 0.8
    assert valid_config.language == "eng"

    # Test invalid confidence value
    with pytest.raises(ValidationError):
        OCRConfig(
            tesseract_path="/usr/local/bin/tesseract",
            min_confidence=1.5  # Invalid: must be between 0 and 1
        )

def test_storage_config_validation(tmp_path):
    """Test storage configuration validation"""
    # Create temporary directories for testing
    upload_dir = tmp_path / "uploads"
    processed_dir = tmp_path / "processed"
    upload_dir.mkdir()
    processed_dir.mkdir()

    # Test valid configuration
    valid_config = StorageConfig(
        upload_path=upload_dir,
        processed_path=processed_dir,
        max_file_size=10_485_760,
        allowed_extensions=[".jpg", ".png", ".pdf"]
    )
    assert valid_config.max_file_size == 10_485_760
    assert ".jpg" in valid_config.allowed_extensions
    
    # Test extension normalization
    config_with_mixed_extensions = StorageConfig(
        upload_path=upload_dir,
        processed_path=processed_dir,
        allowed_extensions=["JPG", ".PNG", "pdf"]
    )
    assert all(ext.startswith('.') for ext in config_with_mixed_extensions.allowed_extensions)
    assert all(ext.islower() for ext in config_with_mixed_extensions.allowed_extensions)

def test_queue_config_validation():
    """Test queue configuration validation"""
    valid_config = QueueConfig(
        worker_count=4,
        task_timeout=600,
        max_retries=3,
        retry_delay=300
    )
    assert valid_config.worker_count == 4
    assert valid_config.task_timeout == 600

def test_settings_from_yaml(tmp_path):
    """Test loading settings from YAML file"""
    config_file = tmp_path / "config.yaml"
    config_content = """
service:
  name: tradeshowscout-ocr
  host: 0.0.0.0
  port: 8000
  debug: true
  environment: development

ocr:
  tesseract_path: /usr/local/bin/tesseract
  min_confidence: 0.8
  max_retries: 3
  timeout: 300
  batch_size: 10
  language: eng

database:
  url: postgresql://localhost:5432/test_db
  pool_size: 5
  max_overflow: 10
  echo: true

redis:
  url: redis://localhost:6379/0
  max_memory: 2gb
  max_memory_policy: allkeys-lru

storage:
  upload_path: /tmp/uploads
  processed_path: /tmp/processed
  max_file_size: 10485760
  allowed_extensions:
    - .jpg
    - .png
    - .pdf

queue:
  worker_count: 4
  task_timeout: 600
  max_retries: 3
  retry_delay: 300

monitoring:
  prometheus_port: 9090
  metrics_path: /metrics
  collection_interval: 15

logging:
  level: DEBUG
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: logs/ocr-service.log
  max_size: 10485760
  backup_count: 5
"""
    config_file.write_text(config_content)
    
    settings = Settings.from_yaml(config_file)
    
    # Verify service settings
    assert settings.service.name == "tradeshowscout-ocr"
    assert settings.service.port == 8000
    
    # Verify OCR settings
    assert settings.ocr.tesseract_path == Path("/usr/local/bin/tesseract")
    assert settings.ocr.min_confidence == 0.8
    
    # Verify storage settings
    assert settings.storage.max_file_size == 10485760
    assert ".jpg" in settings.storage.allowed_extensions
    
    # Verify queue settings
    assert settings.queue.worker_count == 4
    assert settings.queue.task_timeout == 600

def test_settings_environment_override(monkeypatch):
    """Test environment variable override of settings"""
    # Set environment variables
    monkeypatch.setenv("SERVICE_PORT", "9000")
    monkeypatch.setenv("OCR_MIN_CONFIDENCE", "0.9")
    monkeypatch.setenv("QUEUE_WORKER_COUNT", "8")
    
    # Create minimal valid config
    config = {
        "service": {
            "name": "test-service",
            "host": "localhost",
            "port": 8000,  # Should be overridden
            "debug": False,
            "environment": "test"
        },
        "ocr": {
            "tesseract_path": "/usr/local/bin/tesseract",
            "min_confidence": 0.8  # Should be overridden
        },
        "queue": {
            "worker_count": 4  # Should be overridden
        }
    }
    
    settings = Settings(**config)
    
    # Verify environment variables override config file values
    assert settings.service.port == 9000
    assert settings.ocr.min_confidence == 0.9
    assert settings.queue.worker_count == 8