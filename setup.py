# setup.py

from setuptools import setup, find_packages
import os

setup(
    name="bob",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'click>=7.0',
    ],
    entry_points={
        'console_scripts': [
            'bob=bob.cli.main:cli',
        ],
    },
    author="Minkyu Shim", 
    author_email="minkyu.shim@gmail.com",
    description="An AI-assisted software development tool",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/heartonbit/bob",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)