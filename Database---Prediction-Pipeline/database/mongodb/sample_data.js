// Sample Data for MongoDB Collections

// Use the loan prediction database
use loan_prediction_db;

// Sample loan applications
db.loan_applications.insertMany([
    {
        loan_id: "LP001002",
        gender: "Male",
        married: "No",
        dependents: "0",
        education: "Graduate",
        self_employed: "No",
        applicant_income: 5849.0,
        coapplicant_income: 0.0,
        loan_amount: 141.0,
        loan_amount_term: 360,
        credit_history: 1,
        property_area: "Urban",
        loan_status: "Y",
        created_at: new Date("2024-01-01"),
        updated_at: new Date("2024-01-01")
    },
    {
        loan_id: "LP001003",
        gender: "Male",
        married: "Yes",
        dependents: "1",
        education: "Graduate",
        self_employed: "No",
        applicant_income: 4583.0,
        coapplicant_income: 1508.0,
        loan_amount: 128.0,
        loan_amount_term: 360,
        credit_history: 1,
        property_area: "Rural",
        loan_status: "N",
        created_at: new Date("2024-01-02"),
        updated_at: new Date("2024-01-02")
    },
    {
        loan_id: "LP001005",
        gender: "Male",
        married: "Yes",
        dependents: "0",
        education: "Graduate",
        self_employed: "Yes",
        applicant_income: 3000.0,
        coapplicant_income: 0.0,
        loan_amount: 66.0,
        loan_amount_term: 360,
        credit_history: 1,
        property_area: "Urban",
        loan_status: "Y",
        created_at: new Date("2024-01-03"),
        updated_at: new Date("2024-01-03")
    }
]);

// Sample loan predictions
db.loan_predictions.insertMany([
    {
        loan_id: "LP001002",
        predicted_status: "Approved",
        confidence_score: 0.85,
        probability_approved: 0.85,
        model_version: "v1.0",
        feature_importance: {
            "credit_history": 0.25,
            "applicant_income": 0.20,
            "education": 0.15,
            "property_area": 0.10,
            "married": 0.10,
            "dependents": 0.08,
            "self_employed": 0.07,
            "loan_amount": 0.05
        },
        prediction_created_at: new Date("2024-01-01T10:00:00Z")
    },
    {
        loan_id: "LP001003",
        predicted_status: "Rejected",
        confidence_score: 0.78,
        probability_approved: 0.22,
        model_version: "v1.0",
        feature_importance: {
            "credit_history": 0.30,
            "applicant_income": 0.18,
            "education": 0.12,
            "property_area": 0.12,
            "married": 0.10,
            "dependents": 0.08,
            "self_employed": 0.05,
            "loan_amount": 0.05
        },
        prediction_created_at: new Date("2024-01-02T10:00:00Z")
    }
]);

// Sample loan analytics
db.loan_analytics.insertMany([
    {
        analysis_date: new Date("2024-01-01"),
        total_applications: 614,
        approved_loans: 422,
        rejected_loans: 192,
        approval_rate: 68.73,
        avg_applicant_income: 5403.46,
        avg_loan_amount: 146.41,
        gender_distribution: {
            "Male": 489,
            "Female": 112,
            "Unknown": 13
        },
        education_distribution: {
            "Graduate": 480,
            "Not Graduate": 134
        },
        property_area_distribution: {
            "Urban": 202,
            "Semiurban": 207,
            "Rural": 205
        },
        income_ranges: {
            "0-3000": 245,
            "3001-6000": 234,
            "6001-10000": 89,
            "10000+": 46
        },
        analytics_created_at: new Date("2024-01-01T23:59:59Z")
    }
]);

print("Sample data inserted successfully!"); 