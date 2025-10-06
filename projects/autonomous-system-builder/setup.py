#!/usr/bin/env python3
"""
Setup script for Autonomous TDD System

Installs the autonomous test-driven development system for Claude Code
with all necessary dependencies and configuration.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with requirements_path.open(encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="autonomous-tdd",
    version="0.1.0",
    description="Autonomous Test-Driven Development System for Claude Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Autonomous TDD Development Team",
    author_email="autonomous-tdd@example.com",
    url="https://github.com/autonomous-tdd/autonomous-tdd-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0"
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0"
        ],
        "performance": [
            "orjson>=3.8.0",
            "psutil>=5.9.0"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="autonomous testing tdd claude-code development automation",
    entry_points={
        "console_scripts": [
            "autonomous-tdd=autonomous_tdd.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "autonomous_tdd": [
            "config/*.json",
            "config/*.yaml",
            "templates/*.json",
            "schemas/*.json"
        ]
    },
    zip_safe=False,
)