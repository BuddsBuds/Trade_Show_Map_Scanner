"""
Tests for the main application module.
"""
import os
import pytest
from fastapi.testclient import TestClient
import yaml
import asyncio
from pathlib import Path
from unittest.mock import patch

from src.main import create_app, load_config, main

@pytest.fixture
def test_config():
    """Fixture to provide test configuration."""
    config_path = Path("config/testing/config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def test_load_config_development():
    """Test loading development configuration."""
    os.environ["ENVIRONMENT"] = "development"
    config = load_config()
    
    assert config is not None
    assert config["service"]["name"] == "tradeshowscout-ocr"
    assert config["service"]["environment"] == "development"
    assert "database" in config
    assert "redis" in config
    assert "ocr" in config

def test_load_config_testing():
    """Test loading testing configuration."""
    os.environ["ENVIRONMENT"] = "testing"
    config = load_config()
    
    assert config is not None
    assert config["service"]["name"] == "tradeshowscout-ocr"
    assert config["service"]["environment"] == "testing"
    assert config["service"]["port"] == 8001
    assert config["database"]["url"].endswith("tradeshowscout_test")

def test_load_config_invalid_env():
    """Test loading configuration with invalid environment."""
    os.environ["ENVIRONMENT"] = "invalid"
    with pytest.raises(FileNotFoundError) as exc_info:
        load_config()
    assert "Configuration file not found" in str(exc_info.value)

def test_create_app(test_config):
    """Test FastAPI application creation."""
    app = create_app()
    assert app.title == test_config["service"]["name"]
    assert "/api/health" in [route.path for route in app.routes]
    assert "/api/docs" in [route.path for route in app.routes]
    assert app.version == "0.1.0"

def test_health_check_endpoint(test_client, test_config):
    """Test health check endpoint."""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == test_config["service"]["name"]
    assert data["environment"] == test_config["service"]["environment"]

def test_docs_endpoint(test_client):
    """Test API documentation endpoint."""
    response = test_client.get("/api/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@pytest.mark.parametrize("invalid_path", [
    "/health",  # Missing /api prefix
    "/api/invalid",  # Non-existent endpoint
    "/api/",  # Root path
])
def test_invalid_endpoints(test_client, invalid_path):
    """Test handling of invalid endpoints."""
    response = test_client.get(invalid_path)
    assert response.status_code == 404

def test_startup_shutdown_events():
    """Test application startup and shutdown events."""
    app = create_app()
    
    # Test that startup and shutdown event handlers are registered
    startup_handlers = [handler for handler in app.router.on_startup]
    shutdown_handlers = [handler for handler in app.router.on_shutdown]
    
    assert len(startup_handlers) > 0, "No startup handlers found"
    assert len(shutdown_handlers) > 0, "No shutdown handlers found"
    
    # Verify the handler names
    assert any(handler.__name__ == "startup_event" for handler in startup_handlers)
    assert any(handler.__name__ == "shutdown_event" for handler in shutdown_handlers)

@pytest.mark.asyncio
async def test_startup_shutdown_execution():
    """Test execution of startup and shutdown events."""
    app = create_app()
    
    # Get the event handlers
    startup_handler = next(handler for handler in app.router.on_startup)
    shutdown_handler = next(handler for handler in app.router.on_shutdown)
    
    # Execute the handlers
    await startup_handler()
    await shutdown_handler()

def test_main_function():
    """Test the main function."""
    with patch('uvicorn.run') as mock_run:
        main()
        mock_run.assert_called_once()
        
        # Verify uvicorn configuration
        call_args = mock_run.call_args[1]
        assert 'host' in call_args
        assert 'port' in call_args
        assert 'reload' in call_args