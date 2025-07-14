-- Loan Prediction Database Schema
-- MySQL Database Design

-- Create database
CREATE DATABASE IF NOT EXISTS loan_prediction_db;
USE loan_prediction_db;

-- Table 1: Loan Applications (Main table)
CREATE TABLE loan_applications (
    loan_id VARCHAR(20) PRIMARY KEY,
    gender ENUM('Male', 'Female') NOT NULL,
    married ENUM('Yes', 'No') NOT NULL,
    dependents ENUM('0', '1', '2', '3+') NOT NULL,
    education ENUM('Graduate', 'Not Graduate') NOT NULL,
    self_employed ENUM('Yes', 'No') NOT NULL,
    applicant_income DECIMAL(10,2) NOT NULL,
    coapplicant_income DECIMAL(10,2) NOT NULL,
    loan_amount DECIMAL(10,2),
    loan_amount_term INT,
    credit_history TINYINT(1),
    property_area ENUM('Urban', 'Semiurban', 'Rural') NOT NULL,
    loan_status ENUM('Y', 'N') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_loan_status (loan_status),
    INDEX idx_gender (gender),
    INDEX idx_education (education),
    INDEX idx_property_area (property_area)
);

-- Table 2: Loan Features (Derived features for ML)
CREATE TABLE loan_features (
    feature_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id VARCHAR(20) NOT NULL,
    total_income DECIMAL(10,2) NOT NULL,
    income_ratio DECIMAL(5,2),
    loan_to_income_ratio DECIMAL(5,2),
    has_coapplicant BOOLEAN DEFAULT FALSE,
    is_graduate BOOLEAN DEFAULT FALSE,
    is_self_employed BOOLEAN DEFAULT FALSE,
    has_credit_history BOOLEAN DEFAULT FALSE,
    feature_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loan_applications(loan_id) ON DELETE CASCADE,
    INDEX idx_loan_id (loan_id),
    INDEX idx_total_income (total_income)
);

-- Table 3: Loan Predictions (ML predictions)
CREATE TABLE loan_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id VARCHAR(20) NOT NULL,
    predicted_status ENUM('Approved', 'Rejected') NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    probability_approved DECIMAL(5,4) NOT NULL,
    model_version VARCHAR(20) DEFAULT 'v1.0',
    prediction_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loan_applications(loan_id) ON DELETE CASCADE,
    INDEX idx_loan_id (loan_id),
    INDEX idx_predicted_status (predicted_status),
    INDEX idx_confidence_score (confidence_score)
);

-- Table 4: Loan Analytics (Aggregated statistics)
CREATE TABLE loan_analytics (
    analytics_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_date DATE NOT NULL,
    total_applications INT NOT NULL,
    approved_loans INT NOT NULL,
    rejected_loans INT NOT NULL,
    approval_rate DECIMAL(5,2) NOT NULL,
    avg_applicant_income DECIMAL(10,2) NOT NULL,
    avg_loan_amount DECIMAL(10,2) NOT NULL,
    gender_distribution JSON,
    education_distribution JSON,
    property_area_distribution JSON,
    analytics_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (analysis_date),
    INDEX idx_analysis_date (analysis_date)
);

-- Insert sample data from CSV
-- This will be populated by the import script 