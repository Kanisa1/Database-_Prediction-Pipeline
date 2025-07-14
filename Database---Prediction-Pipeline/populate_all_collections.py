import random
from datetime import datetime, date
from pymongo import MongoClient

# MongoDB Atlas connection
mongo_uri = "mongodb+srv://kthiak:XXiwmsnbKekatNos@cluster0.3ra2bhr.mongodb.net/loan_prediction_db?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['loan_prediction_db']

# 1. Populate loan_features
features = []
for app in db.loan_applications.find():
    total_income = app.get('applicant_income', 0) + app.get('coapplicant_income', 0)
    income_ratio = (app.get('applicant_income', 0) / (app.get('coapplicant_income', 1) or 1)) if app.get('coapplicant_income', 0) else None
    has_coapplicant = app.get('coapplicant_income', 0) > 0
    is_graduate = app.get('education', '').lower() == 'graduate'
    is_self_employed = app.get('self_employed', '').lower() == 'yes'
    has_credit_history = app.get('credit_history', 0) == 1
    features.append({
        'loan_id': app['loan_id'],
        'total_income': total_income,
        'income_ratio': income_ratio,
        'has_coapplicant': has_coapplicant,
        'is_graduate': is_graduate,
        'is_self_employed': is_self_employed,
        'has_credit_history': has_credit_history,
        'feature_created_at': datetime.now()
    })
if features:
    db.loan_features.delete_many({})
    db.loan_features.insert_many(features)
    print(f"Inserted {len(features)} documents into loan_features.")

# 2. Populate loan_predictions (simulate predictions)
predictions = []
for app in db.loan_applications.find():
    predicted_status = random.choice(['Approved', 'Rejected'])
    confidence_score = round(random.uniform(0.6, 1.0), 4)
    probability_approved = confidence_score if predicted_status == 'Approved' else 1 - confidence_score
    predictions.append({
        'loan_id': app['loan_id'],
        'predicted_status': predicted_status,
        'confidence_score': confidence_score,
        'probability_approved': probability_approved,
        'model_version': 'v1.0',
        'feature_importance': {},
        'prediction_created_at': datetime.now()
    })
if predictions:
    db.loan_predictions.delete_many({})
    db.loan_predictions.insert_many(predictions)
    print(f"Inserted {len(predictions)} documents into loan_predictions.")

from datetime import datetime


# 3. Populate loan_analytics (basic stats)
total_applications = db.loan_applications.count_documents({})
approved_loans = db.loan_applications.count_documents({'loan_status': 'Y'})
rejected_loans = db.loan_applications.count_documents({'loan_status': 'N'})
approval_rate = round((approved_loans / total_applications) * 100, 2) if total_applications else 0

avg_applicant_income = next(
    db.loan_applications.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$applicant_income'}}}]), {}
).get('avg', 0)
avg_loan_amount = next(
    db.loan_applications.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$loan_amount'}}}]), {}
).get('avg', 0)

def agg_to_dict(cursor, key='_id', value='count'):
    return {doc[key]: doc[value] for doc in cursor if doc[key] is not None}

gender_distribution = agg_to_dict(
    db.loan_applications.aggregate([{'$group': {'_id': '$gender', 'count': {'$sum': 1}}}])
)
education_distribution = agg_to_dict(
    db.loan_applications.aggregate([{'$group': {'_id': '$education', 'count': {'$sum': 1}}}])
)
property_area_distribution = agg_to_dict(
    db.loan_applications.aggregate([{'$group': {'_id': '$property_area', 'count': {'$sum': 1}}}])
)

analytics_doc = {
    'analysis_date': datetime.now(),  # Use datetime, not date
    'total_applications': total_applications,
    'approved_loans': approved_loans,
    'rejected_loans': rejected_loans,
    'approval_rate': approval_rate,
    'avg_applicant_income': avg_applicant_income,
    'avg_loan_amount': avg_loan_amount,
    'gender_distribution': gender_distribution,
    'education_distribution': education_distribution,
    'property_area_distribution': property_area_distribution,
    'income_ranges': {},
    'analytics_created_at': datetime.now()
}
db.loan_analytics.delete_many({})
db.loan_analytics.insert_one(analytics_doc)
print("Inserted analytics document into loan_analytics.")
