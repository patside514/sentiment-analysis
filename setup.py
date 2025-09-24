"""
Setup script for the Social Media Sentiment Analysis application.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sentiment-analysis",
    version="1.0.0",
    author="patside514",
    author_email="patrick.cote234@gmail.com",
    description="A comprehensive tool for analyzing sentiment from social media platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ninjatech-ai/social-media-sentiment-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Marketing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sentiment-analyzer=src.cli:main",
            "social-media-analyzer=app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
