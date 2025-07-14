import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO)

# MySQL connection string (update as needed)
MYSQL_URL = "mysql+mysqlconnector://root:Kanisa@localhost/loan_prediction_db"

try:
    engine = create_engine(MYSQL_URL)
    df = pd.read_sql("SELECT * FROM loan_applications", engine)
    logging.info(f"Loaded {len(df)} rows from MySQL.")
except Exception as e:
    logging.error(f"Failed to load data from MySQL: {e}")
    exit(1)

# Preprocessing: map categorical to numeric, handle missing values, etc.
def preprocess(df):
    df = df.copy()
    df['gender'] = df['gender'].map({'Male': 1, 'Female': 0})
    df['married'] = df['married'].map({'Yes': 1, 'No': 0})
    df['education'] = df['education'].map({'Graduate': 1, 'Not Graduate': 0})
    df['self_employed'] = df['self_employed'].map({'Yes': 1, 'No': 0})
    df['credit_history'] = df['credit_history'].fillna(0)
    df['dependents'] = df['dependents'].map({'0': 0, '1': 1, '2': 2, '3+': 3})
    df['property_area'] = df['property_area'].map({'Urban': 0, 'Semiurban': 1, 'Rural': 2})
    df['applicant_income'] = df['applicant_income'].astype(float)
    df['coapplicant_income'] = df['coapplicant_income'].astype(float)
    df['loan_amount'] = df['loan_amount'].fillna(0).astype(float)
    df['loan_amount_term'] = df['loan_amount_term'].fillna(360).astype(int)
    df['total_income'] = df['applicant_income'] + df['coapplicant_income']
    df['income_to_loan_ratio'] = df.apply(lambda x: x['total_income'] / x['loan_amount'] if x['loan_amount'] else 0, axis=1)
    df['monthly_payment'] = df.apply(lambda x: x['loan_amount'] / x['loan_amount_term'] if x['loan_amount_term'] else 0, axis=1)
    # Target: Y=1, N=0
    df['target'] = df['loan_status'].map({'Y': 1, 'N': 0})
    return df

df = preprocess(df)

feature_names = [
    'gender', 'married', 'education', 'self_employed', 'credit_history',
    'dependents', 'property_area', 'applicant_income', 'coapplicant_income',
    'loan_amount', 'loan_amount_term', 'total_income', 'income_to_loan_ratio', 'monthly_payment'
]

X = df[feature_names]
y = df['target']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Train a simple logistic regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
logging.info(f"Test accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Save the model
os.makedirs('ml', exist_ok=True)
joblib.dump(model, 'ml/loan_prediction_model.pkl')
logging.info("Model saved to ml/loan_prediction_model.pkl") 