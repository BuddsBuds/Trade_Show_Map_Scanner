"""
TradeShow Scout OCR Service - Main Application Entry Point
"""
import os
import yaml
import uvicorn
from fastapi import FastAPI
from pathlib import Path

def load_config():
    """Load service configuration."""
    env = os.getenv("ENVIRONMENT", "development")  # Fixed string concatenation bug
    config_path = Path(f"config/{env}/config.yaml")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()
    
    app = FastAPI(
        title=config["service"]["name"],
        description="OCR service for processing trade show floor plans",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    @app.get("/api/health")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "service": config["service"]["name"],
            "environment": config["service"]["environment"]
        }

    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        # Initialize services here
        pass

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        # Cleanup resources here
        pass

    return app

def main():
    """Main entry point for the OCR service."""
    config = load_config()
    app = create_app()
    
    uvicorn.run(
        app,
        host=config["service"]["host"],
        port=config["service"]["port"],
        reload=config["service"]["debug"]
    )

if __name__ == "__main__":
    main()