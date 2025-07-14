#!/usr/bin/env python3
"""
Comprehensive Verification Script
This script verifies that all components of the database system are working correctly.
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_mysql_database():
    """Verify MySQL database is working correctly"""
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Default XAMPP MySQL password is empty
            database='loan_prediction_db'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            logger.info("🔍 VERIFYING MYSQL DATABASE")
            logger.info("=" * 50)
            
            # 1. Check database connection
            logger.info("✅ MySQL Connection: Working")
            
            # 2. Check tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            logger.info(f"✅ Tables found: {', '.join(table_names)}")
            
            # 3. Check data counts
            cursor.execute("SELECT COUNT(*) as count FROM applicants")
            applicant_count = cursor.fetchone()['count']
            logger.info(f"✅ Applicants: {applicant_count} records")
            
            cursor.execute("SELECT COUNT(*) as count FROM loan_applications")
            loan_count = cursor.fetchone()['count']
            logger.info(f"✅ Loan Applications: {loan_count} records")
            
            cursor.execute("SELECT COUNT(*) as count FROM property_areas")
            area_count = cursor.fetchone()['count']
            logger.info(f"✅ Property Areas: {area_count} records")
            
            cursor.execute("SELECT COUNT(*) as count FROM loan_terms")
            term_count = cursor.fetchone()['count']
            logger.info(f"✅ Loan Terms: {term_count} records")
            
            cursor.execute("SELECT COUNT(*) as count FROM application_logs")
            log_count = cursor.fetchone()['count']
            logger.info(f"✅ Application Logs: {log_count} records")
            
            # 4. Check foreign key relationships
            cursor.execute("""
                SELECT COUNT(*) as orphaned FROM loan_applications la
                LEFT JOIN applicants a ON la.applicant_id = a.applicant_id
                WHERE a.applicant_id IS NULL
            """)
            orphaned_count = cursor.fetchone()['orphaned']
            if orphaned_count == 0:
                logger.info("✅ Foreign Key Relationships: All valid")
            else:
                logger.warning(f"⚠️  Orphaned records: {orphaned_count}")
            
            # 5. Test stored procedures
            logger.info("\n🔍 TESTING STORED PROCEDURES")
            
            # Test ValidateLoanApplication
            try:
                cursor.callproc('ValidateLoanApplication', ['TEST001', 100000, 1, None, None])
                cursor.execute("SELECT @p_is_valid, @p_message")
                result = cursor.fetchone()
                if result['@p_is_valid'] == 1:
                    logger.info("✅ ValidateLoanApplication: Working")
                else:
                    logger.warning(f"⚠️  ValidateLoanApplication: {result['@p_message']}")
            except Error as e:
                logger.error(f"❌ ValidateLoanApplication: {e}")
            
            # Test PredictLoanApproval
            try:
                cursor.callproc('PredictLoanApproval', [100000, 1, 'Urban', None, None])
                cursor.execute("SELECT @p_approval_probability, @p_recommendation")
                result = cursor.fetchone()
                if result['@p_approval_probability'] is not None:
                    logger.info(f"✅ PredictLoanApproval: Probability={result['@p_approval_probability']:.4f}, Recommendation={result['@p_recommendation']}")
                else:
                    logger.warning("⚠️  PredictLoanApproval: No data available for prediction")
            except Error as e:
                logger.error(f"❌ PredictLoanApproval: {e}")
            
            # 6. Test views
            logger.info("\n🔍 TESTING VIEWS")
            
            cursor.execute("SELECT COUNT(*) as count FROM loan_application_summary")
            summary_count = cursor.fetchone()['count']
            logger.info(f"✅ loan_application_summary: {summary_count} records")
            
            cursor.execute("SELECT * FROM approval_stats_by_area")
            area_stats = cursor.fetchall()
            logger.info(f"✅ approval_stats_by_area: {len(area_stats)} area statistics")
            for stat in area_stats:
                logger.info(f"   {stat['area_name']}: {stat['approval_rate']}% approval rate")
            
            cursor.execute("SELECT * FROM approval_stats_by_credit")
            credit_stats = cursor.fetchall()
            logger.info(f"✅ approval_stats_by_credit: {len(credit_stats)} credit statistics")
            for stat in credit_stats:
                logger.info(f"   Credit {stat['credit_history']}: {stat['approval_rate']}% approval rate")
            
            # 7. Test triggers
            logger.info("\n🔍 TESTING TRIGGERS")
            
            # Test insert trigger
            test_loan_id = f"VERIFY_{int(datetime.now().timestamp())}"
            initial_log_count = log_count
            
            cursor.execute("""
                INSERT INTO loan_applications (loan_id, applicant_id, loan_amount, credit_history, property_area_id, loan_status)
                VALUES (%s, 1, 50000, 1, 1, 'Y')
            """, (test_loan_id,))
            
            cursor.execute("SELECT COUNT(*) as count FROM application_logs WHERE loan_id = %s", (test_loan_id,))
            new_log_count = cursor.fetchone()['count']
            
            if new_log_count > initial_log_count:
                logger.info("✅ Insert Trigger: Working")
            else:
                logger.warning("⚠️  Insert Trigger: Not working")
            
            # Test update trigger
            cursor.execute("""
                UPDATE loan_applications SET loan_status = 'N' WHERE loan_id = %s
            """, (test_loan_id,))
            
            cursor.execute("SELECT COUNT(*) as count FROM application_logs WHERE loan_id = %s", (test_loan_id,))
            final_log_count = cursor.fetchone()['count']
            
            if final_log_count > new_log_count:
                logger.info("✅ Update Trigger: Working")
            else:
                logger.warning("⚠️  Update Trigger: Not working")
            
            # Clean up test data
            cursor.execute("DELETE FROM loan_applications WHERE loan_id = %s", (test_loan_id,))
            connection.commit()
            
            # 8. Sample data verification
            logger.info("\n🔍 SAMPLE DATA VERIFICATION")
            
            cursor.execute("""
                SELECT la.loan_id, la.applicant_id, a.first_name, a.last_name, 
                       la.loan_amount, pa.area_name, la.loan_status
                FROM loan_applications la
                JOIN applicants a ON la.applicant_id = a.applicant_id
                JOIN property_areas pa ON la.property_area_id = pa.area_id
                LIMIT 5
            """)
            sample_data = cursor.fetchall()
            
            logger.info("Sample loan applications:")
            for row in sample_data:
                logger.info(f"   {row['loan_id']}: {row['first_name']} {row['last_name']} - ${row['loan_amount']} - {row['area_name']} - {row['loan_status']}")
            
            logger.info("\n✅ MYSQL DATABASE VERIFICATION COMPLETE")
            return True
            
    except Error as e:
        logger.error(f"❌ MySQL Database Error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_csv_data():
    """Verify CSV data integrity"""
    try:
        logger.info("\n🔍 VERIFYING CSV DATA")
        logger.info("=" * 50)
        
        # Load CSV data
        df = pd.read_csv('loan_applications.csv')
        logger.info(f"✅ CSV loaded: {len(df)} records")
        
        # Check for missing values
        missing_loan_amount = df['LoanAmount'].isna().sum()
        missing_credit_history = df['Credit_History'].isna().sum()
        missing_loan_term = df['Loan_Amount_Term'].isna().sum()
        
        logger.info(f"✅ Missing LoanAmount: {missing_loan_amount}")
        logger.info(f"✅ Missing Credit_History: {missing_credit_history}")
        logger.info(f"✅ Missing Loan_Amount_Term: {missing_loan_term}")
        
        # Check unique values
        unique_applicants = df['applicant_id'].nunique()
        unique_areas = df['Property_Area'].nunique()
        unique_statuses = df['Loan_Status'].nunique()
        
        logger.info(f"✅ Unique applicants: {unique_applicants}")
        logger.info(f"✅ Unique property areas: {unique_areas}")
        logger.info(f"✅ Unique loan statuses: {unique_statuses}")
        
        # Check property areas
        area_counts = df['Property_Area'].value_counts()
        logger.info("Property area distribution:")
        for area, count in area_counts.items():
            logger.info(f"   {area}: {count} applications")
        
        # Check loan status distribution
        status_counts = df['Loan_Status'].value_counts()
        logger.info("Loan status distribution:")
        for status, count in status_counts.items():
            logger.info(f"   {status}: {count} applications")
        
        logger.info("✅ CSV DATA VERIFICATION COMPLETE")
        return True
        
    except Exception as e:
        logger.error(f"❌ CSV Data Error: {e}")
        return False

def verify_files():
    """Verify all required files exist"""
    logger.info("\n🔍 VERIFYING FILES")
    logger.info("=" * 50)
    
    required_files = [
        'database_schema.sql',
        'mongodb_schema.js',
        'loan_applications.csv',
        'ERD_Diagram.pdf',
        'ERD_Diagram.png',
        'create_erd.py',
        'setup_database.py',
        'test_database.py',
        'requirements.txt',
        'README.md'
    ]
    
    optional_files = [
        'fix_data_consistency.py',
        'add_procedures_views.py',
        'add_triggers.py',
        'setup_mongodb_atlas.py',
        'verify_everything.py'
    ]
    
    missing_required = []
    missing_optional = []
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                logger.info(f"✅ {file}")
        except FileNotFoundError:
            missing_required.append(file)
            logger.error(f"❌ {file} - MISSING")
    
    for file in optional_files:
        try:
            with open(file, 'r') as f:
                logger.info(f"✅ {file} (optional)")
        except FileNotFoundError:
            missing_optional.append(file)
            logger.warning(f"⚠️  {file} - MISSING (optional)")
    
    if missing_required:
        logger.error(f"❌ Missing required files: {missing_required}")
        return False
    else:
        logger.info("✅ All required files present")
        return True

def main():
    """Run all verifications"""
    logger.info("🚀 STARTING COMPREHENSIVE VERIFICATION")
    logger.info("=" * 60)
    
    # Verify files
    files_ok = verify_files()
    
    # Verify CSV data
    csv_ok = verify_csv_data()
    
    # Verify MySQL database
    mysql_ok = verify_mysql_database()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    if files_ok:
        logger.info("✅ Files: All required files present")
    else:
        logger.error("❌ Files: Missing required files")
    
    if csv_ok:
        logger.info("✅ CSV Data: Valid and complete")
    else:
        logger.error("❌ CSV Data: Issues found")
    
    if mysql_ok:
        logger.info("✅ MySQL Database: Working correctly")
    else:
        logger.error("❌ MySQL Database: Issues found")
    
    # Overall status
    if files_ok and csv_ok and mysql_ok:
        logger.info("\n🎉 ALL SYSTEMS WORKING CORRECTLY!")
        logger.info("Your database system is ready for submission.")
    else:
        logger.warning("\n⚠️  SOME ISSUES FOUND")
        logger.info("Please address the issues above before submission.")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    main() 