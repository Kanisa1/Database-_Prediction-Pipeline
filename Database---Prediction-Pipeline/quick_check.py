#!/usr/bin/env python3
"""
Quick Database Check Script
Simple script to quickly verify if databases are accessible and have data.
"""

import mysql.connector
import pymongo
from pymongo import MongoClient
import sys

def check_mysql():
    """Quick MySQL check"""
    print("🔍 Checking MySQL...")
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='loan_prediction_db'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Check if database exists
        cursor.execute("SELECT DATABASE() as current_db")
        db_name = cursor.fetchone()['current_db']
        print(f"✅ Connected to database: {db_name}")
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(table.values())[0] for table in tables]
        print(f"✅ Found {len(table_names)} tables: {', '.join(table_names)}")
        
        # Check loan applications count
        cursor.execute("SELECT COUNT(*) as count FROM loan_applications")
        count = cursor.fetchone()['count']
        print(f"✅ Loan applications: {count} records")
        
        # Test a stored procedure
        cursor.callproc('ValidateLoanApplication', ['TEST', 100000, 1, None, None])
        cursor.execute("SELECT @p_is_valid, @p_message")
        result = cursor.fetchone()
        print(f"✅ Stored procedure test: Valid={result['@p_is_valid']}, Message={result['@p_message']}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL check failed: {e}")
        return False

def check_mongodb():
    """Quick MongoDB check"""
    print("\n🔍 Checking MongoDB...")
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client['loan_prediction_db']
        print("✅ Connected to MongoDB")
        
        # Check collections
        collections = db.list_collection_names()
        print(f"✅ Found {len(collections)} collections: {', '.join(collections)}")
        
        # Check loan applications count
        count = db.loan_applications.count_documents({})
        print(f"✅ Loan applications: {count} documents")
        
        # Test aggregation
        pipeline = [{'$group': {'_id': '$property_area', 'count': {'$sum': 1}}}]
        results = list(db.loan_applications.aggregate(pipeline))
        print(f"✅ Aggregation test: {len(results)} area groups found")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB check failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Quick Database Check")
    print("=" * 40)
    
    mysql_ok = check_mysql()
    mongo_ok = check_mongodb()
    
    print("\n" + "=" * 40)
    if mysql_ok and mongo_ok:
        print("🎉 Both databases are working correctly!")
        print("✅ You can now run the full test suite with: python test_database.py")
        return 0
    else:
        print("⚠️  Some database checks failed.")
        print("💡 Make sure:")
        print("   - MySQL server is running on localhost:3306")
        print("   - MongoDB server is running on localhost:27017")
        print("   - Database credentials are correct")
        print("   - You've run the setup scripts first")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
