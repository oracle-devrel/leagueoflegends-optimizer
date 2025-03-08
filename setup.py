"""
Setup script for the League Optimizer package.
"""
from setuptools import find_packages, setup

setup(
    name="leagueoptimizer",
    version="0.1.0",
    description="League of Legends Optimizer - A tool for predicting game outcomes",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/oracle-devrel/leagueoflegends-optimizer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "ujson>=5.7.0",
        "numpy==1.23",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "pandas>=2.0.3",
        "autogluon>=1.1.1",
        "oracledb>=1.4.1",
        "pika>=1.3.2",
        "python-dotenv>=1.0.0",
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "leagueoptimizer=leagueoptimizer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Universal Permissive License (UPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 