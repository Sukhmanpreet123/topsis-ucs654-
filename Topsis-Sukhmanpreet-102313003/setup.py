from setuptools import setup, find_packages
import os

# Read the User Manual from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Topsis-Sukhmanpreet-102313003",
    version="1.0.0",
    author="Sukhmanpreet Kaur",
    author_email="sukhmanpreetkaur102313003@gmail.com",
    description="A Python package for implementing TOPSIS technique.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sukhmanpreet123/topsis-ucs654-", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            # This must match the folder name '102313003' shown in your image
            'topsis=102313003.topsis:main',
        ],
    },
)