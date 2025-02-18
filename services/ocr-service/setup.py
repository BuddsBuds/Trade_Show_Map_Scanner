from setuptools import setup, find_packages
import os

def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read requirements
requirements = read_requirements('requirements.txt')

setup(
    name="tradeshowscout-ocr",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=requirements,
    package_data={
        "tradeshowscout_ocr": [
            "config/development/*.yaml",
            "config/testing/*.yaml",
        ],
    },
    entry_points={
        "console_scripts": [
            "tradeshowscout-ocr=tradeshowscout_ocr.main:main",
        ],
    },
    author="TradeShow Scout Team",
    author_email="team@tradeshowscout.com",
    description="OCR service for processing trade show floor plans",
    keywords="ocr,tradeshow,image processing",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)