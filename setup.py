#!/usr/bin/env python3
"""
Setup script for Server Monitor application.

This script allows the Server Monitor to be installed as a Python package,
making it easier to distribute and manage dependencies.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="server-monitor",
    version="1.0.0",
    author="Server Monitor Team",
    author_email="admin@example.com",
    description="A comprehensive server monitoring application with GUI and alerting capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/server-monitor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "cx-freeze>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "server-monitor=monitor_server.main:main",
            "server-monitor-gui=monitor_server.gui.main_window:main",
            "server-monitor-console=monitor_server.console:main",
        ],
    },
    include_package_data=True,
    package_data={
        "monitor_server": [
            "config/*.json",
            "data/*.csv",
            "logs/*.log",
        ],
    },
    zip_safe=False,
    keywords="server monitoring network ping http status gui alerts telemetry",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/server-monitor/issues",
        "Source": "https://github.com/yourusername/server-monitor",
        "Documentation": "https://github.com/yourusername/server-monitor/blob/main/README.md",
    },
)