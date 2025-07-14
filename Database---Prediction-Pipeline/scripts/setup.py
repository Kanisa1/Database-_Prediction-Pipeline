#!/usr/bin/env python3
"""
Setup script for Loan Prediction Pipeline
Initializes the project structure and dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data",
        "ml",
        "api",
        "database/mysql",
        "database/mongodb",
        "docs",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=loan_prediction_db

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=loan_prediction_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✓ Created .env file")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pandas",
        "scikit-learn",
        "python-dotenv",
        "pydantic",
        "joblib",
        "sqlalchemy",
        "pymongo",
        "mysql-connector-python"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} is missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r api/requirements.txt")
        return False
    
    return True

def check_dataset():
    """Check if the loan prediction dataset exists"""
    dataset_path = "data/loan_prediction.csv"
    
    if os.path.exists(dataset_path):
        print(f"✓ Dataset found: {dataset_path}")
        return True
    else:
        print(f"✗ Dataset not found: {dataset_path}")
        print("Please place the loan_prediction.csv file in the data/ directory")
        return False

def create_sample_data():
    """Create sample data for testing"""
    sample_data = """Loan_ID,Gender,Married,Dependents,Education,Self_Employed,ApplicantIncome,CoapplicantIncome,LoanAmount,Loan_Amount_Term,Credit_History,Property_Area,Loan_Status
LP001002,Male,No,0,Graduate,No,5849,0,141,360,1,Urban,Y
LP001003,Male,Yes,1,Graduate,No,4583,1508,128,360,1,Rural,N
LP001005,Male,Yes,0,Graduate,Yes,3000,0,66,360,1,Urban,Y
LP001006,Male,Yes,0,Not Graduate,No,2583,2358,120,360,1,Urban,Y
LP001008,Male,No,0,Graduate,No,6000,0,141,360,1,Urban,Y"""
    
    with open("data/loan_prediction.csv", "w") as f:
        f.write(sample_data)
    print("✓ Created sample dataset")

def run_tests():
    """Run basic tests to verify setup"""
    print("\n=== Running Setup Tests ===")
    
    # Test 1: Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✓ Python version: {python_version.major}.{python_version.minor}")
    else:
        print(f"✗ Python version {python_version.major}.{python_version.minor} is too old. Need 3.8+")
        return False
    
    # Test 2: Check dependencies
    if not check_dependencies():
        return False
    
    # Test 3: Check dataset
    if not check_dataset():
        create_sample_data()
    
    # Test 4: Test imports
    try:
        import pandas as pd
        import sklearn
        import fastapi
        print("✓ All core modules can be imported")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=== Loan Prediction Pipeline Setup ===")
    
    # Create directories
    print("\n1. Creating project structure...")
    create_directories()
    
    # Create .env file
    print("\n2. Creating configuration files...")
    create_env_file()
    
    # Run tests
    print("\n3. Running setup tests...")
    if run_tests():
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your database settings in .env file")
        print("2. Install dependencies: pip install -r api/requirements.txt")
        print("3. Train the model: python ml/model_training.py")
        print("4. Start the API: python api/main.py")
        print("5. Run predictions: python ml/prediction_script.py")
    else:
        print("\n❌ Setup failed! Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 