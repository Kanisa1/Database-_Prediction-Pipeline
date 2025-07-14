// MongoDB Collections for Loan Prediction System

// Use the loan prediction database
use loan_prediction_db;

// Collection 1: Loan Applications (Document storage)
db.createCollection("loan_applications", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["loan_id", "gender", "married", "dependents", "education", "self_employed", "applicant_income", "coapplicant_income", "property_area", "loan_status"],
            properties: {
                loan_id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                gender: {
                    enum: ["Male", "Female"],
                    description: "must be either Male or Female"
                },
                married: {
                    enum: ["Yes", "No"],
                    description: "must be either Yes or No"
                },
                dependents: {
                    enum: ["0", "1", "2", "3+"],
                    description: "must be one of the specified values"
                },
                education: {
                    enum: ["Graduate", "Not Graduate"],
                    description: "must be either Graduate or Not Graduate"
                },
                self_employed: {
                    enum: ["Yes", "No"],
                    description: "must be either Yes or No"
                },
                applicant_income: {
                    bsonType: "double",
                    minimum: 0,
                    description: "must be a positive number"
                },
                coapplicant_income: {
                    bsonType: "double",
                    minimum: 0,
                    description: "must be a non-negative number"
                },
                loan_amount: {
                    bsonType: ["double", "null"],
                    minimum: 0,
                    description: "must be a positive number or null"
                },
                loan_amount_term: {
                    bsonType: ["int", "null"],
                    minimum: 0,
                    description: "must be a positive integer or null"
                },
                credit_history: {
                    bsonType: ["int", "null"],
                    minimum: 0,
                    maximum: 1,
                    description: "must be 0, 1, or null"
                },
                property_area: {
                    enum: ["Urban", "Semiurban", "Rural"],
                    description: "must be one of the specified values"
                },
                loan_status: {
                    enum: ["Y", "N"],
                    description: "must be either Y or N"
                },
                created_at: {
                    bsonType: "date",
                    description: "must be a date"
                },
                updated_at: {
                    bsonType: "date",
                    description: "must be a date"
                }
            }
        }
    }
});

// Collection 2: Loan Predictions (ML predictions)
db.createCollection("loan_predictions", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["loan_id", "predicted_status", "confidence_score", "probability_approved", "model_version"],
            properties: {
                loan_id: {
                    bsonType: "string",
                    description: "must be a string and is required"
                },
                predicted_status: {
                    enum: ["Approved", "Rejected"],
                    description: "must be either Approved or Rejected"
                },
                confidence_score: {
                    bsonType: "double",
                    minimum: 0,
                    maximum: 1,
                    description: "must be between 0 and 1"
                },
                probability_approved: {
                    bsonType: "double",
                    minimum: 0,
                    maximum: 1,
                    description: "must be between 0 and 1"
                },
                model_version: {
                    bsonType: "string",
                    description: "must be a string"
                },
                feature_importance: {
                    bsonType: "object",
                    description: "feature importance scores"
                },
                prediction_created_at: {
                    bsonType: "date",
                    description: "must be a date"
                }
            }
        }
    }
});

// Collection 3: Loan Analytics (Aggregated statistics)
db.createCollection("loan_analytics", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["analysis_date", "total_applications", "approved_loans", "rejected_loans", "approval_rate"],
            properties: {
                analysis_date: {
                    bsonType: "date",
                    description: "must be a date"
                },
                total_applications: {
                    bsonType: "int",
                    minimum: 0,
                    description: "must be a non-negative integer"
                },
                approved_loans: {
                    bsonType: "int",
                    minimum: 0,
                    description: "must be a non-negative integer"
                },
                rejected_loans: {
                    bsonType: "int",
                    minimum: 0,
                    description: "must be a non-negative integer"
                },
                approval_rate: {
                    bsonType: "double",
                    minimum: 0,
                    maximum: 100,
                    description: "must be between 0 and 100"
                },
                avg_applicant_income: {
                    bsonType: "double",
                    minimum: 0,
                    description: "must be a positive number"
                },
                avg_loan_amount: {
                    bsonType: "double",
                    minimum: 0,
                    description: "must be a positive number"
                },
                gender_distribution: {
                    bsonType: "object",
                    description: "gender distribution statistics"
                },
                education_distribution: {
                    bsonType: "object",
                    description: "education distribution statistics"
                },
                property_area_distribution: {
                    bsonType: "object",
                    description: "property area distribution statistics"
                },
                income_ranges: {
                    bsonType: "object",
                    description: "income range distribution"
                },
                analytics_created_at: {
                    bsonType: "date",
                    description: "must be a date"
                }
            }
        }
    }
});

// Create indexes for better performance
db.loan_applications.createIndex({ "loan_id": 1 }, { unique: true });
db.loan_applications.createIndex({ "loan_status": 1 });
db.loan_applications.createIndex({ "gender": 1 });
db.loan_applications.createIndex({ "education": 1 });
db.loan_applications.createIndex({ "property_area": 1 });
db.loan_applications.createIndex({ "created_at": 1 });

db.loan_predictions.createIndex({ "loan_id": 1 });
db.loan_predictions.createIndex({ "predicted_status": 1 });
db.loan_predictions.createIndex({ "confidence_score": 1 });
db.loan_predictions.createIndex({ "prediction_created_at": 1 });

db.loan_analytics.createIndex({ "analysis_date": 1 }, { unique: true });
db.loan_analytics.createIndex({ "approval_rate": 1 });

print("MongoDB collections created successfully!"); 