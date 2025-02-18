from setuptools import setup, find_packages

setup(
    name="file-processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-multipart>=0.0.6",
        "pillow>=10.1.0",
        "pypdf2>=3.0.1",
        "pytest>=7.4.3",
        "httpx>=0.25.1",
        "python-jose[cryptography]>=3.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "pytest-asyncio>=0.21.1",
        "aiofiles>=23.2.1",
        "pytest-cov>=4.1.0"
    ],
    python_requires=">=3.11"
)