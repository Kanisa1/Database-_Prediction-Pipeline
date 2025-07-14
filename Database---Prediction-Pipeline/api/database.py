"""
Database connection module for Loan Prediction System
Handles connections to both MySQL and MongoDB databases
"""

import os
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean, Text, JSON, ForeignKey, Enum, DECIMAL, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from mysql.connector.cursor import MySQLCursorDict

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# MySQL Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Kanisa")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "loan_prediction_db")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "loan_prediction_db")

# MySQL Connection
MYSQL_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine = create_engine(MYSQL_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB Connection
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DATABASE]

class DatabaseManager:
    """Manages database connections for both MySQL and MongoDB"""
    
    def __init__(self):
        self.mysql_connection = None
        self.mongodb_client = None
        self.mongodb_db = None
        
    def connect_mysql(self) -> bool:
        """Establish connection to MySQL database"""
        try:
            self.mysql_connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', 'Kanisa'),
                database=os.getenv('MYSQL_DATABASE', 'loan_prediction_db'),
                autocommit=True
            )
            
            if self.mysql_connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
            else:
                logger.error("Failed to connect to MySQL database")
                return False
                
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def connect_mongodb(self) -> bool:
        """Establish connection to MongoDB Atlas"""
        try:
            # Get MongoDB connection string from environment
            mongo_uri = os.getenv('MONGODB_URI')
            if not mongo_uri:
                logger.error("MONGODB_URI environment variable not set")
                return False
            
            self.mongodb_client = MongoClient(mongo_uri)
            
            # Test the connection
            self.mongodb_client.admin.command('ping')
            
            # Get database
            db_name = os.getenv('MONGODB_DATABASE', 'loan_prediction_db')
            self.mongodb_db = self.mongodb_client[db_name]
            
            logger.info("Successfully connected to MongoDB Atlas")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def get_mysql_connection(self):
        """Get MySQL connection, reconnect if necessary"""
        if self.mysql_connection is None or not self.mysql_connection.is_connected():
            self.connect_mysql()
        return self.mysql_connection
    
    def get_mongodb_db(self):
        """Get MongoDB database instance"""
        if self.mongodb_db is None:
            self.connect_mongodb()
        return self.mongodb_db
    
    def close_mysql(self):
        """Close MySQL connection"""
        if self.mysql_connection and self.mysql_connection.is_connected():
            self.mysql_connection.close()
            logger.info("MySQL connection closed")
    
    def close_mongodb(self):
        """Close MongoDB connection"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("MongoDB connection closed")
    
    def close_all(self):
        """Close all database connections"""
        self.close_mysql()
        self.close_mongodb()

# Global database manager instance
db_manager = DatabaseManager()

def get_mysql_connection():
    """Get MySQL connection for dependency injection"""
    return db_manager.get_mysql_connection()

def get_mongodb_db():
    """Get MongoDB database for dependency injection"""
    return db_manager.get_mongodb_db()

# Database utility functions
class MySQLRepository:
    """Repository pattern for MySQL operations"""
    
    def __init__(self, connection):
        self.connection = connection
        self.cursor: Optional[MySQLCursorDict] = None
    
    def __enter__(self):
        self.cursor = self.connection.cursor(dictionary=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
    
    def execute_query(self, query: str, params: tuple = ()):
        if self.cursor is None:
            raise RuntimeError("MySQLRepository: cursor is not initialized.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def execute_procedure(self, procedure_name: str, params: tuple = ( )):
        if self.cursor is None:
            raise RuntimeError("MySQLRepository: cursor is not initialized.")
        try:
            if params:
                self.cursor.callproc(procedure_name, params)
            else:
                self.cursor.callproc(procedure_name)
            # Get results from all result sets
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results
        except Error as e:
            logger.error(f"Error executing procedure {procedure_name}: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = () ):
        if self.cursor is None:
            raise RuntimeError("MySQLRepository: cursor is not initialized.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.lastrowid
        except Error as e:
            logger.error(f"Error executing insert: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = () ):
        if self.cursor is None:
            raise RuntimeError("MySQLRepository: cursor is not initialized.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.rowcount
        except Error as e:
            logger.error(f"Error executing update: {e}")
            raise

class MongoDBRepository:
    """Repository pattern for MongoDB operations"""
    
    def __init__(self, db):
        from typing import Any
        self.db: Optional[Any] = db
    
    def find_one(self, collection: str, filter_dict: dict):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            return self.db[collection].find_one(filter_dict)
        except Exception as e:
            logger.error(f"Error finding document in {collection}: {e}")
            raise
    
    def find_many(self, collection: str, filter_dict: dict = {}, limit: int = 0):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            cursor = self.db[collection].find(filter_dict)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {e}")
            raise
    
    def insert_one(self, collection: str, document: dict):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            result = self.db[collection].insert_one(document)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document into {collection}: {e}")
            raise
    
    def insert_many(self, collection: str, documents: list):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            result = self.db[collection].insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            logger.error(f"Error inserting documents into {collection}: {e}")
            raise
    
    def update_one(self, collection: str, filter_dict: dict, update_dict: dict):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            result = self.db[collection].update_one(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {e}")
            raise
    
    def delete_one(self, collection: str, filter_dict: dict):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            result = self.db[collection].delete_one(filter_dict)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {e}")
            raise
    
    def aggregate(self, collection: str, pipeline: list):
        if self.db is None:
            raise RuntimeError("MongoDBRepository: db is not initialized.")
        try:
            return list(self.db[collection].aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error executing aggregation in {collection}: {e}")
            raise

def check_mysql_health() -> dict:
    """Check MySQL database health"""
    try:
        connection = get_mysql_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return {"status": "healthy", "message": "MySQL connection successful"}
        else:
            return {"status": "unhealthy", "message": "MySQL connection failed"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"MySQL health check failed: {str(e)}"}

def check_mongodb_health() -> dict:
    """Check MongoDB database health"""
    try:
        db = get_mongodb_db()
        if db is not None:
            db.command('ping')
            return {"status": "healthy", "message": "MongoDB connection successful"}
        else:
            return {"status": "unhealthy", "message": "MongoDB connection is None"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"MongoDB health check failed: {str(e)}"}

def check_all_databases() -> dict:
    """Check health of all databases"""
    mysql_health = check_mysql_health()
    mongodb_health = check_mongodb_health()
    
    overall_status = "healthy" if (
        mysql_health["status"] == "healthy" and 
        mongodb_health["status"] == "healthy"
    ) else "unhealthy"
    
    return {
        "overall_status": overall_status,
        "mysql": mysql_health,
        "mongodb": mongodb_health
    }

# Database Models
class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(String(20), unique=True, nullable=False, index=True)
    gender = Column(Enum('Male', 'Female', name='gender_enum'), nullable=True)
    married = Column(Enum('Yes', 'No', name='married_enum'), nullable=True)
    dependents = Column(Enum('0', '1', '2', '3+', name='dependents_enum'), nullable=True)
    education = Column(Enum('Graduate', 'Not Graduate', name='education_enum'), nullable=True)
    self_employed = Column(Enum('Yes', 'No', name='self_employed_enum'), nullable=True)
    applicant_income = Column(DECIMAL(12, 2), nullable=False)
    coapplicant_income = Column(DECIMAL(12, 2), nullable=False)
    loan_amount = Column(DECIMAL(12, 2), nullable=True)
    loan_amount_term = Column(Integer, nullable=True)
    credit_history = Column(Integer, nullable=False)
    property_area = Column(Enum('Urban', 'Rural', 'Semiurban', name='property_area_enum'), nullable=True)
    loan_status = Column(Enum('Y', 'N', name='loan_status_enum'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    features = relationship("LoanFeature", back_populates="loan_application", cascade="all, delete-orphan")
    predictions = relationship("LoanPrediction", back_populates="loan_application", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('applicant_income >= 0', name='check_applicant_income_positive'),
        CheckConstraint('coapplicant_income >= 0', name='check_coapplicant_income_positive'),
        CheckConstraint('loan_amount >= 0', name='check_loan_amount_positive'),
        CheckConstraint('loan_amount_term > 0', name='check_loan_amount_term_positive'),
        CheckConstraint('credit_history IN (0, 1)', name='check_credit_history_binary'),
    )

class LoanFeature(Base):
    __tablename__ = "loan_features"
    
    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), ForeignKey("loan_applications.loan_id"), nullable=False)
    total_income = Column(DECIMAL(10, 2), nullable=False)
    income_ratio = Column(DECIMAL(5, 2), nullable=True)
    loan_to_income_ratio = Column(DECIMAL(5, 2), nullable=True)
    has_coapplicant = Column(Boolean, default=False)
    is_graduate = Column(Boolean, default=False)
    is_self_employed = Column(Boolean, default=False)
    has_credit_history = Column(Boolean, default=False)
    feature_created_at = Column(DateTime, default=func.now())
    
    # Relationships
    loan_application = relationship("LoanApplication", back_populates="features", foreign_keys=[loan_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint('loan_id IS NOT NULL', name='check_loan_id_not_null'),
    )



class LoanAnalytics(Base):
    __tablename__ = "loan_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(Date, nullable=False, index=True)
    total_applications = Column(Integer, nullable=False)
    approved_loans = Column(Integer, nullable=False)
    rejected_loans = Column(Integer, nullable=False)
    approval_rate = Column(DECIMAL(5, 2), nullable=False)
    avg_loan_amount = Column(DECIMAL(12, 2), nullable=True)
    avg_applicant_income = Column(DECIMAL(12, 2), nullable=True)
    avg_coapplicant_income = Column(DECIMAL(12, 2), nullable=True)
    gender_distribution = Column(JSON, nullable=True)
    education_distribution = Column(JSON, nullable=True)
    property_area_distribution = Column(JSON, nullable=True)
    income_ranges = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_applications >= 0', name='check_total_applications_positive'),
        CheckConstraint('approved_loans >= 0', name='check_approved_loans_positive'),
        CheckConstraint('rejected_loans >= 0', name='check_rejected_loans_positive'),
        CheckConstraint('approval_rate >= 0 AND approval_rate <= 100', name='check_approval_rate_range'),
    )

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo_collections():
    """Get MongoDB collections"""
    return mongo_db.list_collection_names()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine) 