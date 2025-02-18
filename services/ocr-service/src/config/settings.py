from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings, DirectoryPath, FilePath, HttpUrl, validator

class ServiceConfig(BaseSettings):
    """Base service configuration"""
    name: str
    host: str
    port: int
    debug: bool
    environment: str

    class Config:
        env_prefix = "SERVICE_"

class OCRConfig(BaseSettings):
    """OCR-specific configuration"""
    tesseract_path: FilePath
    min_confidence: float = 0.8
    max_retries: int = 3
    timeout: int = 300
    batch_size: int = 10
    language: str = "eng"

    @validator('min_confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    class Config:
        env_prefix = "OCR_"

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    class Config:
        env_prefix = "DB_"

class RedisConfig(BaseSettings):
    """Redis configuration"""
    url: str
    max_memory: str = "2gb"
    max_memory_policy: str = "allkeys-lru"

    class Config:
        env_prefix = "REDIS_"

class StorageConfig(BaseSettings):
    """Storage configuration"""
    upload_path: DirectoryPath
    processed_path: DirectoryPath
    max_file_size: int = 10_485_760  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]

    @validator('allowed_extensions')
    def validate_extensions(cls, v):
        return [ext.lower() if not ext.startswith('.') else ext.lower() for ext in v]

    class Config:
        env_prefix = "STORAGE_"

class QueueConfig(BaseSettings):
    """Queue configuration"""
    worker_count: int = 4
    task_timeout: int = 600
    max_retries: int = 3
    retry_delay: int = 300

    class Config:
        env_prefix = "QUEUE_"

class MonitoringConfig(BaseSettings):
    """Monitoring configuration"""
    prometheus_port: int = 9090
    metrics_path: str = "/metrics"
    collection_interval: int = 15

    class Config:
        env_prefix = "MONITORING_"

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[Path] = None
    max_size: int = 10_485_760  # 10MB
    backup_count: int = 5

    class Config:
        env_prefix = "LOGGING_"

class Settings(BaseSettings):
    """Global settings container"""
    service: ServiceConfig
    ocr: OCRConfig
    database: DatabaseConfig
    redis: RedisConfig
    storage: StorageConfig
    queue: QueueConfig
    monitoring: MonitoringConfig
    logging: LoggingConfig

    @classmethod
    def from_yaml(cls, yaml_path: Path):
        """Load settings from YAML file"""
        import yaml
        with open(yaml_path) as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)