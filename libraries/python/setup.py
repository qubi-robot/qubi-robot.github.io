from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qubi-protocol",
    version="1.0.0",
    author="Qubi Project",
    author_email="qubi@example.com",
    description="Python library for Qubi robot communication protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qubi-robot/qubi-robot.github.io",
    project_urls={
        "Bug Tracker": "https://github.com/qubi-robot/qubi-robot.github.io/issues",
        "Documentation": "https://qubi-robot.github.io",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        "Topic :: Communications",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "examples": [
            "asyncio-mqtt>=0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qubi-discover=qubi_protocol.cli:discover_command",
            "qubi-send=qubi_protocol.cli:send_command",
        ],
    },
)