#!/usr/bin/env python3
"""
Quick Data Import Script - No .env file needed
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickDataImporter:
    def __init__(self):
        self.mysql_connection = None
        self.mongodb_client = None
        self.mongodb_db = None
        
    def connect_mysql(self):
        """Connect to MySQL database"""
        try:
            self.mysql_connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Kanisa@123',
    database='loan_prediction_db',
    autocommit=True,
    auth_plugin='mysql_native_password'
)
            
            if self.mysql_connection.is_connected():
                logger.info("✅ Successfully connected to MySQL database")
                return True
            else:
                logger.error("❌ Failed to connect to MySQL database")
                return False
                
        except Error as e:
            logger.error(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def connect_mongodb(self):
        """Connect to MongoDB database"""
        try:
            # Your MongoDB Atlas connection string
            mongo_uri = "mongodb+srv://kthiak:XXiwmsnbKekatNos@cluster0.3ra2bhr.mongodb.net/loan_prediction_db?retryWrites=true&w=majority"
            
            self.mongodb_client = MongoClient(mongo_uri)
            
            # Test the connection
            self.mongodb_client.admin.command('ping')
            
            # Get database
            self.mongodb_db = self.mongodb_client['loan_prediction_db']
            
            logger.info("✅ Successfully connected to MongoDB")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Error connecting to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            return False
    
    def load_csv_data(self, file_path='data/loan_prediction.csv'):
        """Load CSV data"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"📊 Loaded {len(df)} records from CSV file")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading CSV file: {e}")
            return None
    
    def clean_data(self, df):
        """Clean and preprocess the data"""
        logger.info("🧹 Cleaning data...")
        
        # Handle missing values
        df = df.fillna({
            'Gender': 'Male',
            'Married': 'No',
            'Dependents': '0',
            'Education': 'Graduate',
            'Self_Employed': 'No',
            'LoanAmount': df['LoanAmount'].median(),
            'Loan_Amount_Term': df['Loan_Amount_Term'].median(),
            'Credit_History': 1
        })
        
        # Convert data types
        df['ApplicantIncome'] = pd.to_numeric(df['ApplicantIncome'], errors='coerce')
        df['CoapplicantIncome'] = pd.to_numeric(df['CoapplicantIncome'], errors='coerce')
        df['LoanAmount'] = pd.to_numeric(df['LoanAmount'], errors='coerce')
        df['Loan_Amount_Term'] = pd.to_numeric(df['Loan_Amount_Term'], errors='coerce')
        df['Credit_History'] = pd.to_numeric(df['Credit_History'], errors='coerce')
        
        # Fill remaining NaN values
        df = df.fillna({
            'ApplicantIncome': df['ApplicantIncome'].median(),
            'CoapplicantIncome': df['CoapplicantIncome'].median(),
            'LoanAmount': df['LoanAmount'].median(),
            'Loan_Amount_Term': df['Loan_Amount_Term'].median(),
            'Credit_History': 1
        })
        
        logger.info(f"✅ Data cleaned. Shape: {df.shape}")
        return df
    
    def import_to_mysql(self, df):
        """Import data to MySQL database"""
        if not self.mysql_connection or not self.mysql_connection.is_connected():
            logger.error("❌ MySQL connection not available")
            return False
        
        try:
            cursor = self.mysql_connection.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM loan_applications")
            logger.info("🗑️ Cleared existing data from loan_applications table")
            
            # Insert data
            insert_query = """
            INSERT INTO loan_applications (
                loan_id, gender, married, dependents, education, self_employed,
                applicant_income, coapplicant_income, loan_amount, loan_amount_term,
                credit_history, property_area, loan_status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            records_inserted = 0
            for _, row in df.iterrows():
                values = (
                    row['Loan_ID'],
                    row['Gender'],
                    row['Married'],
                    row['Dependents'],
                    row['Education'],
                    row['Self_Employed'],
                    float(row['ApplicantIncome']),
                    float(row['CoapplicantIncome']),
                    float(row['LoanAmount']) if pd.notna(row['LoanAmount']) else None,
                    int(row['Loan_Amount_Term']) if pd.notna(row['Loan_Amount_Term']) else None,
                    int(row['Credit_History']) if pd.notna(row['Credit_History']) else None,
                    row['Property_Area'],
                    row['Loan_Status'],
                    datetime.now(),
                    datetime.now()
                )
                
                cursor.execute(insert_query, values)
                records_inserted += 1
                
                if records_inserted % 100 == 0:
                    logger.info(f"📝 Inserted {records_inserted} records...")
            
            cursor.close()
            logger.info(f"✅ Successfully imported {records_inserted} records to MySQL")
            return True
            
        except Error as e:
            logger.error(f"❌ Error importing to MySQL: {e}")
            return False
    
    def import_to_mongodb(self, df):
        """Import data to MongoDB database"""
        if self.mongodb_db is None:
            logger.error("❌ MongoDB connection not available")
            return False
        
        try:
            # Clear existing data
            self.mongodb_db.loan_applications.delete_many({})
            logger.info("🗑️ Cleared existing data from MongoDB loan_applications collection")
            
            # Convert DataFrame to list of dictionaries
            records = []
            for _, row in df.iterrows():
                record = {
                    'loan_id': row['Loan_ID'],
                    'gender': row['Gender'],
                    'married': row['Married'],
                    'dependents': row['Dependents'],
                    'education': row['Education'],
                    'self_employed': row['Self_Employed'],
                    'applicant_income': float(row['ApplicantIncome']),
                    'coapplicant_income': float(row['CoapplicantIncome']),
                    'loan_amount': float(row['LoanAmount']) if pd.notna(row['LoanAmount']) else None,
                    'loan_amount_term': int(row['Loan_Amount_Term']) if pd.notna(row['Loan_Amount_Term']) else None,
                    'credit_history': int(row['Credit_History']) if pd.notna(row['Credit_History']) else None,
                    'property_area': row['Property_Area'],
                    'loan_status': row['Loan_Status'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                records.append(record)
            
            # Insert data in batches
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                result = self.mongodb_db.loan_applications.insert_many(batch)
                total_inserted += len(result.inserted_ids)
                logger.info(f"📝 Inserted {total_inserted} records to MongoDB...")
            
            logger.info(f"✅ Successfully imported {total_inserted} records to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error importing to MongoDB: {e}")
            return False
    
    def verify_import(self):
        """Verify the data import"""
        logger.info("🔍 Verifying data import...")
        
        # Check MySQL
        if self.mysql_connection and self.mysql_connection.is_connected():
            cursor = self.mysql_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM loan_applications")
            result = cursor.fetchone()
            cursor.close()
            
            mysql_count = "Unknown"
            if result is not None:
                result_list = list(result)
                if len(result_list) > 0:
                    mysql_count = str(result_list[0])
            
            logger.info(f"📊 MySQL: {mysql_count} records found")
        else:
            logger.warning("⚠️ MySQL connection not available for verification")
        
        # Check MongoDB
        if self.mongodb_db is not None:
            mongo_count = self.mongodb_db.loan_applications.count_documents({})
            logger.info(f"📊 MongoDB: {mongo_count} records found")
        else:
            logger.warning("⚠️ MongoDB connection not available for verification")
    
    def close_connections(self):
        """Close database connections"""
        if self.mysql_connection and self.mysql_connection.is_connected():
            self.mysql_connection.close()
            logger.info("🔌 MySQL connection closed")
        
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("🔌 MongoDB connection closed")

def main():
    """Main function to import data"""
    print("🚀 === QUICK LOAN PREDICTION DATA IMPORT ===")
    
    importer = QuickDataImporter()
    
    try:
        # Connect to databases
        print("\n1️⃣ Connecting to databases...")
        mysql_connected = importer.connect_mysql()
        mongo_connected = importer.connect_mongodb()
        
        if not mysql_connected and not mongo_connected:
            print("❌ Failed to connect to any database!")
            return
        
        # Load and clean data
        print("\n2️⃣ Loading and cleaning data...")
        df = importer.load_csv_data()
        if df is None:
            print("❌ Failed to load CSV data!")
            return
        
        df = importer.clean_data(df)
        
        # Import to databases
        print("\n3️⃣ Importing data to databases...")
        
        if mysql_connected:
            print("📝 Importing to MySQL...")
            mysql_success = importer.import_to_mysql(df)
            if mysql_success:
                print("✅ MySQL import successful")
            else:
                print("❌ MySQL import failed")
        
        if mongo_connected:
            print("📝 Importing to MongoDB...")
            mongo_success = importer.import_to_mongodb(df)
            if mongo_success:
                print("✅ MongoDB import successful")
            else:
                print("❌ MongoDB import failed")
        
        # Verify import
        print("\n4️⃣ Verifying import...")
        importer.verify_import()
        
        print("\n🎉 === DATA IMPORT COMPLETED SUCCESSFULLY! ===")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"❌ Import failed: {e}")
    
    finally:
        importer.close_connections()

if __name__ == "__main__":
    main() 