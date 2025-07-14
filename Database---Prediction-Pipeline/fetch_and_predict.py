import requests
import joblib
import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

API_URL = "http://127.0.0.1:8000/loans/?skip=0&limit=1"
MODEL_PATH = "ml/loan_prediction_model.pkl"

feature_names = [
    'gender', 'married', 'education', 'self_employed', 'credit_history',
    'dependents', 'property_area', 'applicant_income', 'coapplicant_income',
    'loan_amount', 'loan_amount_term', 'total_income', 'income_to_loan_ratio', 'monthly_payment'
]

def prepare_features(loan):
    try:
        features = {}
        features['gender'] = 1 if loan["gender"] == "Male" else 0
        features['married'] = 1 if loan["married"] == "Yes" else 0
        features['education'] = 1 if loan["education"] == "Graduate" else 0
        features['self_employed'] = 1 if loan["self_employed"] == "Yes" else 0
        features['credit_history'] = loan["credit_history"] if loan["credit_history"] is not None else 0
        dependents_map = {"0": 0, "1": 1, "2": 2, "3+": 3}
        features['dependents'] = dependents_map.get(loan["dependents"], 0)
        property_map = {"Urban": 0, "Semiurban": 1, "Rural": 2}
        features['property_area'] = property_map.get(loan["property_area"], 0)
        features['applicant_income'] = float(loan["applicant_income"])
        features['coapplicant_income'] = float(loan["coapplicant_income"])
        features['loan_amount'] = float(loan["loan_amount"]) if loan["loan_amount"] is not None else 0
        features['loan_amount_term'] = int(loan["loan_amount_term"]) if loan["loan_amount_term"] is not None else 360
        total_income = features['applicant_income'] + features['coapplicant_income']
        features['total_income'] = total_income
        features['income_to_loan_ratio'] = total_income / features['loan_amount'] if features['loan_amount'] else 0
        features['monthly_payment'] = features['loan_amount'] / features['loan_amount_term'] if features['loan_amount_term'] else 0
        return pd.DataFrame([features])
    except Exception as e:
        logging.error(f"Error preparing features: {e}")
        raise

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    loans = response.json()
    if not loans:
        logging.error("No loan applications found.")
        exit(1)
    latest_loan = loans[-1]
    logging.info(f"Latest loan application: {latest_loan}")
except Exception as e:
    logging.error(f"Failed to fetch data from API: {e}")
    exit(1)

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    exit(1)

try:
    X = prepare_features(latest_loan)
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0].max()
    logging.info(f"Prediction: {'Approved' if prediction == 1 else 'Rejected'} (Confidence: {probability:.2f})")
except Exception as e:
    logging.error(f"Prediction failed: {e}")
    exit(1) 