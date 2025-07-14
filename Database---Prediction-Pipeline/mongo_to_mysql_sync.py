import os
import mysql.connector
from pymongo import MongoClient
from datetime import datetime

# --- CONFIG ---
MONGO_URI = "mongodb+srv://kthiak:XXiwmsnbKekatNos@cluster0.3ra2bhr.mongodb.net/loan_prediction_db?retryWrites=true&w=majority"
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Kanisa',
    'database': 'loan_prediction_db',
    'autocommit': True
}

# --- CONNECT ---
client = MongoClient(MONGO_URI)
db = client['loan_prediction_db']
mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
cursor = mysql_conn.cursor()

# --- 1. loan_features ---
cursor.execute("DELETE FROM loan_features")
features = db.loan_features.find()
for feat in features:
    cursor.execute(
        """
        INSERT INTO loan_features (
            loan_id, total_income, income_ratio, has_coapplicant, is_graduate, is_self_employed, has_credit_history, feature_created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            feat.get('loan_id'),
            float(feat.get('total_income', 0)),
            float(feat.get('income_ratio', 0)) if feat.get('income_ratio') is not None else None,
            int(bool(feat.get('has_coapplicant', False))),
            int(bool(feat.get('is_graduate', False))),
            int(bool(feat.get('is_self_employed', False))),
            int(bool(feat.get('has_credit_history', False))),
            feat.get('feature_created_at', datetime.now())
        )
    )
print("Inserted loan_features into MySQL.")

# --- 2. loan_predictions ---
cursor.execute("DELETE FROM loan_predictions")
preds = db.loan_predictions.find()
for pred in preds:
    cursor.execute(
        """
        INSERT INTO loan_predictions (
            loan_id, predicted_status, confidence_score, probability_approved, model_version, prediction_created_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            pred.get('loan_id'),
            pred.get('predicted_status'),
            float(pred.get('confidence_score', 0)),
            float(pred.get('probability_approved', 0)),
            pred.get('model_version', 'v1.0'),
            pred.get('prediction_created_at', datetime.now())
        )
    )
print("Inserted loan_predictions into MySQL.")

# --- 3. loan_analytics ---
cursor.execute("DELETE FROM loan_analytics")
analytics = db.loan_analytics.find()
for ana in analytics:
    cursor.execute(
        """
        INSERT INTO loan_analytics (
            analysis_date, total_applications, approved_loans, rejected_loans, approval_rate, avg_applicant_income, avg_loan_amount, analytics_created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            ana.get('analysis_date', datetime.now()),
            int(ana.get('total_applications', 0)),
            int(ana.get('approved_loans', 0)),
            int(ana.get('rejected_loans', 0)),
            float(ana.get('approval_rate', 0)),
            float(ana.get('avg_applicant_income', 0)),
            float(ana.get('avg_loan_amount', 0)),
            ana.get('analytics_created_at', datetime.now())
        )
    )
print("Inserted loan_analytics into MySQL.")

cursor.close()
mysql_conn.close()
print("All MongoDB data synced to MySQL!") 