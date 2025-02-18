"""
Tests for service dependencies (PostgreSQL, Redis, Tesseract).
"""
import os
import pytest
import redis
import psycopg2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import io

def test_postgres_dev_connection():
    """Test connection to development database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="tradeshowscout_dev",
            host="localhost",
            port=5432
        )
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
    except Exception as e:
        pytest.fail(f"Failed to connect to development database: {str(e)}")
    finally:
        if conn:
            conn.close()

def test_postgres_test_connection():
    """Test connection to test database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="tradeshowscout_test",
            host="localhost",
            port=5432
        )
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
    except Exception as e:
        pytest.fail(f"Failed to connect to test database: {str(e)}")
    finally:
        if conn:
            conn.close()

def test_redis_connection():
    """Test Redis connection and configuration."""
    r = None
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        assert r.ping()

        # Test Redis configuration
        config = r.config_get('maxmemory')
        assert int(config['maxmemory']) == 2147483648  # 2GB in bytes
        
        config = r.config_get('maxmemory-policy')
        assert config['maxmemory-policy'] == 'allkeys-lru'

        # Test basic operations
        r.set('test_key', 'test_value')
        assert r.get('test_key') == b'test_value'
        r.delete('test_key')
    except Exception as e:
        pytest.fail(f"Failed to connect to Redis: {str(e)}")
    finally:
        if r:
            r.close()

def test_tesseract_availability():
    """Test Tesseract OCR installation and basic functionality."""
    img = None
    img_buffer = None
    try:
        # Create a simple test image with text
        img = Image.new('RGB', (800, 200), color='white')
        d = ImageDraw.Draw(img)
        
        # Simple test text
        test_text = "123"
        
        # Add text to the image with large size for better recognition
        d.text((50, 50), test_text, fill='black', width=5)
        
        # Save to bytes buffer with high quality
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=100)
        img_buffer.seek(0)
        
        # Read image from buffer
        test_image = Image.open(img_buffer)
        
        # Perform OCR with improved configuration
        text = pytesseract.image_to_string(
            test_image,
            config='--psm 7 --oem 1'  # Treat as single line of text
        ).strip()
        
        # Print actual result for debugging
        print(f"OCR Result: '{text}'")
        
        # Simple numeric test
        assert test_text in text
        
        # Test available languages
        langs = pytesseract.get_languages()
        assert 'eng' in langs  # English should be available
        
    except Exception as e:
        pytest.fail(f"Failed to use Tesseract OCR: {str(e)}")
    finally:
        if img:
            img.close()
        if img_buffer:
            img_buffer.close()

def test_service_environment():
    """Test service environment configuration."""
    r = None
    try:
        # Test PostgreSQL environment
        assert os.environ.get('PGHOST', 'localhost') == 'localhost'
        assert os.environ.get('PGPORT', '5432') == '5432'
        
        # Verify Redis host and port are accessible
        r = redis.Redis(host='localhost', port=6379, db=0)
        assert r.ping()
        
        # Verify Tesseract is in PATH
        version_str = str(pytesseract.get_tesseract_version())
        major_version = int(version_str.split('.')[0])
        assert major_version >= 5  # We installed version 5.5.0
    finally:
        if r:
            r.close()