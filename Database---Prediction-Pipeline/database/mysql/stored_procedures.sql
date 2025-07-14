-- Stored Procedures for Loan Prediction Database

USE loan_prediction_db;

-- Procedure 1: Insert new loan application with validation
DELIMITER //
CREATE PROCEDURE InsertLoanApplication(
    IN p_loan_id VARCHAR(20),
    IN p_gender ENUM('Male', 'Female'),
    IN p_married ENUM('Yes', 'No'),
    IN p_dependents ENUM('0', '1', '2', '3+'),
    IN p_education ENUM('Graduate', 'Not Graduate'),
    IN p_self_employed ENUM('Yes', 'No'),
    IN p_applicant_income DECIMAL(10,2),
    IN p_coapplicant_income DECIMAL(10,2),
    IN p_loan_amount DECIMAL(10,2),
    IN p_loan_amount_term INT,
    IN p_credit_history TINYINT(1),
    IN p_property_area ENUM('Urban', 'Semiurban', 'Rural'),
    IN p_loan_status ENUM('Y', 'N')
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Validate input data
    IF p_applicant_income <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Applicant income must be greater than 0';
    END IF;
    
    IF p_loan_amount_term <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan amount term must be greater than 0';
    END IF;
    
    -- Insert loan application
    INSERT INTO loan_applications (
        loan_id, gender, married, dependents, education, self_employed,
        applicant_income, coapplicant_income, loan_amount, loan_amount_term,
        credit_history, property_area, loan_status
    ) VALUES (
        p_loan_id, p_gender, p_married, p_dependents, p_education, p_self_employed,
        p_applicant_income, p_coapplicant_income, p_loan_amount, p_loan_amount_term,
        p_credit_history, p_property_area, p_loan_status
    );
    
    -- Calculate and insert derived features
    INSERT INTO loan_features (
        loan_id, total_income, income_ratio, loan_to_income_ratio,
        has_coapplicant, is_graduate, is_self_employed, has_credit_history
    ) VALUES (
        p_loan_id,
        p_applicant_income + p_coapplicant_income,
        CASE WHEN p_applicant_income > 0 THEN p_coapplicant_income / p_applicant_income ELSE 0 END,
        CASE WHEN (p_applicant_income + p_coapplicant_income) > 0 THEN p_loan_amount / (p_applicant_income + p_coapplicant_income) ELSE 0 END,
        p_coapplicant_income > 0,
        p_education = 'Graduate',
        p_self_employed = 'Yes',
        p_credit_history = 1
    );
    
    COMMIT;
    
    SELECT 'Loan application inserted successfully' AS message;
END //
DELIMITER ;

-- Procedure 2: Get loan statistics
DELIMITER //
CREATE PROCEDURE GetLoanStatistics()
BEGIN
    SELECT 
        COUNT(*) as total_applications,
        SUM(CASE WHEN loan_status = 'Y' THEN 1 ELSE 0 END) as approved_loans,
        SUM(CASE WHEN loan_status = 'N' THEN 1 ELSE 0 END) as rejected_loans,
        ROUND((SUM(CASE WHEN loan_status = 'Y' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as approval_rate,
        ROUND(AVG(applicant_income), 2) as avg_applicant_income,
        ROUND(AVG(loan_amount), 2) as avg_loan_amount
    FROM loan_applications;
END //
DELIMITER ;

-- Procedure 3: Get predictions by confidence level
DELIMITER //
CREATE PROCEDURE GetPredictionsByConfidence(IN min_confidence DECIMAL(5,4))
BEGIN
    SELECT 
        lp.loan_id,
        la.gender,
        la.education,
        la.property_area,
        lp.predicted_status,
        lp.confidence_score,
        lp.probability_approved,
        lp.prediction_created_at
    FROM loan_predictions lp
    JOIN loan_applications la ON lp.loan_id = la.loan_id
    WHERE lp.confidence_score >= min_confidence
    ORDER BY lp.confidence_score DESC;
END //
DELIMITER ;

-- Procedure 4: Update loan application
DELIMITER //
CREATE PROCEDURE UpdateLoanApplication(
    IN p_loan_id VARCHAR(20),
    IN p_applicant_income DECIMAL(10,2),
    IN p_coapplicant_income DECIMAL(10,2),
    IN p_loan_amount DECIMAL(10,2),
    IN p_loan_status ENUM('Y', 'N')
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Update loan application
    UPDATE loan_applications 
    SET 
        applicant_income = p_applicant_income,
        coapplicant_income = p_coapplicant_income,
        loan_amount = p_loan_amount,
        loan_status = p_loan_status,
        updated_at = CURRENT_TIMESTAMP
    WHERE loan_id = p_loan_id;
    
    -- Update derived features
    UPDATE loan_features 
    SET 
        total_income = p_applicant_income + p_coapplicant_income,
        income_ratio = CASE WHEN p_applicant_income > 0 THEN p_coapplicant_income / p_applicant_income ELSE 0 END,
        loan_to_income_ratio = CASE WHEN (p_applicant_income + p_coapplicant_income) > 0 THEN p_loan_amount / (p_applicant_income + p_coapplicant_income) ELSE 0 END,
        has_coapplicant = p_coapplicant_income > 0,
        feature_created_at = CURRENT_TIMESTAMP
    WHERE loan_id = p_loan_id;
    
    COMMIT;
    
    SELECT 'Loan application updated successfully' AS message;
END //
DELIMITER ;

-- Procedure 5: Generate daily analytics
DELIMITER //
CREATE PROCEDURE GenerateDailyAnalytics()
BEGIN
    INSERT INTO loan_analytics (
        analysis_date,
        total_applications,
        approved_loans,
        rejected_loans,
        approval_rate,
        avg_applicant_income,
        avg_loan_amount,
        gender_distribution,
        education_distribution,
        property_area_distribution
    )
    SELECT 
        CURDATE() as analysis_date,
        COUNT(*) as total_applications,
        SUM(CASE WHEN loan_status = 'Y' THEN 1 ELSE 0 END) as approved_loans,
        SUM(CASE WHEN loan_status = 'N' THEN 1 ELSE 0 END) as rejected_loans,
        ROUND((SUM(CASE WHEN loan_status = 'Y' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as approval_rate,
        ROUND(AVG(applicant_income), 2) as avg_applicant_income,
        ROUND(AVG(loan_amount), 2) as avg_loan_amount,
        JSON_OBJECT(
            'Male', SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END),
            'Female', SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END)
        ) as gender_distribution,
        JSON_OBJECT(
            'Graduate', SUM(CASE WHEN education = 'Graduate' THEN 1 ELSE 0 END),
            'Not Graduate', SUM(CASE WHEN education = 'Not Graduate' THEN 1 ELSE 0 END)
        ) as education_distribution,
        JSON_OBJECT(
            'Urban', SUM(CASE WHEN property_area = 'Urban' THEN 1 ELSE 0 END),
            'Semiurban', SUM(CASE WHEN property_area = 'Semiurban' THEN 1 ELSE 0 END),
            'Rural', SUM(CASE WHEN property_area = 'Rural' THEN 1 ELSE 0 END)
        ) as property_area_distribution
    FROM loan_applications
    ON DUPLICATE KEY UPDATE
        total_applications = VALUES(total_applications),
        approved_loans = VALUES(approved_loans),
        rejected_loans = VALUES(rejected_loans),
        approval_rate = VALUES(approval_rate),
        avg_applicant_income = VALUES(avg_applicant_income),
        avg_loan_amount = VALUES(avg_loan_amount),
        gender_distribution = VALUES(gender_distribution),
        education_distribution = VALUES(education_distribution),
        property_area_distribution = VALUES(property_area_distribution),
        analytics_created_at = CURRENT_TIMESTAMP;
END //
DELIMITER ; 