# Entity Relationship Diagram (ERD) - Loan Prediction Database

## Database Schema Overview

The loan prediction system uses a hybrid approach with both MySQL (relational) and MongoDB (NoSQL) databases to store and manage loan application data, predictions, and analytics.
Demonstrates a 1 to 1 relationship between and among each of the 4 tables(loan_applications, loan_features etc)

## MySQL Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        LOAN_APPLICATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│ PK: loan_id (VARCHAR(20))                                       │
│ gender (ENUM: Male, Female)                                     │
│ married (ENUM: Yes, No)                                         │
│ dependents (ENUM: 0, 1, 2, 3+)                                  │
│ education (ENUM: Graduate, Not Graduate)                        │
│ self_employed (ENUM: Yes, No)                                   │
│ applicant_income (DECIMAL(10,2))                                │
│ coapplicant_income (DECIMAL(10,2))                              │
│ loan_amount (DECIMAL(10,2))                                     │
│ loan_amount_term (INT)                                          │
│ credit_history (TINYINT(1))                                     │
│ property_area (ENUM: Urban, Semiurban, Rural)                   │
│ loan_status (ENUM: Y, N)                                        │
│ created_at (TIMESTAMP)                                          │
│ updated_at (TIMESTAMP)                                          │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        │ 1:1
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         LOAN_FEATURES                           │
├─────────────────────────────────────────────────────────────────┤
│ PK: feature_id (INT AUTO_INCREMENT)                             │
│ FK: loan_id (VARCHAR(20)) → loan_applications.loan_id           │
│ total_income (DECIMAL(10,2))                                    │
│ income_ratio (DECIMAL(5,2))                                     │
│ loan_to_income_ratio (DECIMAL(5,2))                             │
│ has_coapplicant (BOOLEAN)                                       │
│ is_graduate (BOOLEAN)                                           │
│ is_self_employed (BOOLEAN)                                      │
│ has_credit_history (BOOLEAN)                                    │
│ feature_created_at (TIMESTAMP)                                  │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        │ 1:1
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LOAN_PREDICTIONS                          │
├─────────────────────────────────────────────────────────────────┤
│ PK: prediction_id (INT AUTO_INCREMENT)                          │
│ FK: loan_id (VARCHAR(20)) → loan_applications.loan_id           │
│ predicted_status (ENUM: Approved, Rejected)                     │
│ confidence_score (DECIMAL(5,4))                                 │
│ probability_approved (DECIMAL(5,4))                             │
│ model_version (VARCHAR(20))                                     │
│ prediction_created_at (TIMESTAMP)                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        LOAN_ANALYTICS                           │
├─────────────────────────────────────────────────────────────────┤
│ PK: analytics_id (INT AUTO_INCREMENT)                           │
│ analysis_date (DATE) UNIQUE                                     │
│ total_applications (INT)                                        │
│ approved_loans (INT)                                            │
│ rejected_loans (INT)                                            │
│ approval_rate (DECIMAL(5,2))                                    │
│ avg_applicant_income (DECIMAL(10,2))                            │
│ avg_loan_amount (DECIMAL(10,2))                                 │
│ gender_distribution (JSON)                                      │
│ education_distribution (JSON)                                   │
│ property_area_distribution (JSON)                               │
│ analytics_created_at (TIMESTAMP)                                │
└─────────────────────────────────────────────────────────────────┘
```

## MongoDB Collections Schema

### Document Structure

#### 1. loan_applications Collection
```json
{
  "_id": ObjectId,
  "loan_id": "LP001002",
  "gender": "Male",
  "married": "No",
  "dependents": "0",
  "education": "Graduate",
  "self_employed": "No",
  "applicant_income": 5849.0,
  "coapplicant_income": 0.0,
  "loan_amount": 141.0,
  "loan_amount_term": 360,
  "credit_history": 1,
  "property_area": "Urban",
  "loan_status": "Y",
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

#### 2. loan_predictions Collection
```json
{
  "_id": ObjectId,
  "loan_id": "LP001002",
  "predicted_status": "Approved",
  "confidence_score": 0.85,
  "probability_approved": 0.85,
  "model_version": "v1.0",
  "feature_importance": {
    "credit_history": 0.25,
    "applicant_income": 0.20,
    "education": 0.15,
    "property_area": 0.10,
    "married": 0.10,
    "dependents": 0.08,
    "self_employed": 0.07,
    "loan_amount": 0.05
  },
  "prediction_created_at": ISODate("2024-01-01T10:00:00Z")
}
```

#### 3. loan_analytics Collection
```json
{
  "_id": ObjectId,
  "analysis_date": ISODate("2024-01-01T00:00:00Z"),
  "total_applications": 614,
  "approved_loans": 422,
  "rejected_loans": 192,
  "approval_rate": 68.73,
  "avg_applicant_income": 5403.46,
  "avg_loan_amount": 146.41,
  "gender_distribution": {
    "Male": 489,
    "Female": 112,
    "Unknown": 13
  },
  "education_distribution": {
    "Graduate": 480,
    "Not Graduate": 134
  },
  "property_area_distribution": {
    "Urban": 202,
    "Semiurban": 207,
    "Rural": 205
  },
  "income_ranges": {
    "0-3000": 245,
    "3001-6000": 234,
    "6001-10000": 89,
    "10000+": 46
  },
  "analytics_created_at": ISODate("2024-01-01T23:59:59Z")
}
```

## Key Relationships

### MySQL Relationships
1. **loan_applications** → **loan_features** (1:1)
   - Primary key: `loan_id`
   - Foreign key constraint with CASCADE delete

2. **loan_applications** → **loan_predictions** (1:1)
   - Primary key: `loan_id`
   - Foreign key constraint with CASCADE delete

3. **loan_analytics** (Independent)
   - No foreign key relationships
   - Contains aggregated statistics

### MongoDB Relationships
- Collections are loosely coupled
- Documents reference each other via `loan_id` field
- No enforced foreign key constraints (NoSQL flexibility)

## Indexes

### MySQL Indexes
- `idx_loan_status` on `loan_applications.loan_status`
- `idx_gender` on `loan_applications.gender`
- `idx_education` on `loan_applications.education`
- `idx_property_area` on `loan_applications.property_area`
- `idx_loan_id` on `loan_features.loan_id`
- `idx_total_income` on `loan_features.total_income`
- `idx_predicted_status` on `loan_predictions.predicted_status`
- `idx_confidence_score` on `loan_predictions.confidence_score`
- `idx_analysis_date` on `loan_analytics.analysis_date`

### MongoDB Indexes
- Unique index on `loan_applications.loan_id`
- Indexes on `loan_status`, `gender`, `education`, `property_area`
- Indexes on `predicted_status`, `confidence_score`
- Unique index on `loan_analytics.analysis_date`

## Data Flow

1. **Data Ingestion**: CSV data → MySQL `loan_applications` table
2. **Feature Engineering**: Automatic calculation → MySQL `loan_features` table
3. **ML Prediction**: Model inference → MySQL `loan_predictions` table
4. **Analytics**: Aggregated statistics → MySQL `loan_analytics` table
5. **Document Storage**: Parallel storage → MongoDB collections
6. **API Access**: FastAPI endpoints serve data from both databases

## Constraints and Validation

### MySQL Constraints
- Primary key constraints on all tables
- Foreign key constraints with CASCADE delete
- ENUM constraints for categorical data
- CHECK constraints for numerical ranges
- NOT NULL constraints on required fields

### MongoDB Validation
- JSON schema validation on collections
- Required field validation
- Enum value validation
- Numeric range validation
- Data type validation

## Audit Tables
- `loan_application_audit`: Tracks changes to loan applications
- `prediction_audit`: Tracks prediction history

This hybrid approach provides the benefits of both relational (ACID compliance, complex queries) and NoSQL (flexibility, scalability) databases for the loan prediction system. 
