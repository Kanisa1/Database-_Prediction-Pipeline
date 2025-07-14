-- Triggers for Loan Prediction Database

USE loan_prediction_db;

-- Trigger 1: Validate loan application before insert
DELIMITER //
CREATE TRIGGER before_loan_application_insert
BEFORE INSERT ON loan_applications
FOR EACH ROW
BEGIN
    -- Validate applicant income
    IF NEW.applicant_income <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Applicant income must be greater than 0';
    END IF;
    
    -- Validate coapplicant income
    IF NEW.coapplicant_income < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Coapplicant income cannot be negative';
    END IF;
    
    -- Validate loan amount term
    IF NEW.loan_amount_term IS NOT NULL AND NEW.loan_amount_term <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan amount term must be greater than 0';
    END IF;
    
    -- Validate credit history
    IF NEW.credit_history IS NOT NULL AND NEW.credit_history NOT IN (0, 1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Credit history must be 0 or 1';
    END IF;
    
    -- Set default values for missing data
    IF NEW.loan_amount IS NULL THEN
        SET NEW.loan_amount = 0;
    END IF;
    
    IF NEW.loan_amount_term IS NULL THEN
        SET NEW.loan_amount_term = 360;
    END IF;
    
    IF NEW.credit_history IS NULL THEN
        SET NEW.credit_history = 1;
    END IF;
END //
DELIMITER ;

-- Trigger 2: Log loan application changes
DELIMITER //
CREATE TRIGGER after_loan_application_update
AFTER UPDATE ON loan_applications
FOR EACH ROW
BEGIN
    -- Log changes to a separate audit table (if exists)
    INSERT INTO loan_application_audit (
        loan_id,
        change_type,
        old_loan_status,
        new_loan_status,
        old_applicant_income,
        new_applicant_income,
        changed_at
    ) VALUES (
        NEW.loan_id,
        'UPDATE',
        OLD.loan_status,
        NEW.loan_status,
        OLD.applicant_income,
        NEW.applicant_income,
        NOW()
    );
END //
DELIMITER ;

-- Trigger 3: Auto-calculate derived features after loan application insert
DELIMITER //
CREATE TRIGGER after_loan_application_insert
AFTER INSERT ON loan_applications
FOR EACH ROW
BEGIN
    -- Insert derived features automatically
    INSERT INTO loan_features (
        loan_id,
        total_income,
        income_ratio,
        loan_to_income_ratio,
        has_coapplicant,
        is_graduate,
        is_self_employed,
        has_credit_history
    ) VALUES (
        NEW.loan_id,
        NEW.applicant_income + NEW.coapplicant_income,
        CASE WHEN NEW.applicant_income > 0 THEN NEW.coapplicant_income / NEW.applicant_income ELSE 0 END,
        CASE WHEN (NEW.applicant_income + NEW.coapplicant_income) > 0 THEN NEW.loan_amount / (NEW.applicant_income + NEW.coapplicant_income) ELSE 0 END,
        NEW.coapplicant_income > 0,
        NEW.education = 'Graduate',
        NEW.self_employed = 'Yes',
        NEW.credit_history = 1
    );
END //
DELIMITER ;

-- Trigger 4: Update derived features when loan application is updated
DELIMITER //
CREATE TRIGGER after_loan_application_update_features
AFTER UPDATE ON loan_applications
FOR EACH ROW
BEGIN
    -- Update derived features
    UPDATE loan_features 
    SET 
        total_income = NEW.applicant_income + NEW.coapplicant_income,
        income_ratio = CASE WHEN NEW.applicant_income > 0 THEN NEW.coapplicant_income / NEW.applicant_income ELSE 0 END,
        loan_to_income_ratio = CASE WHEN (NEW.applicant_income + NEW.coapplicant_income) > 0 THEN NEW.loan_amount / (NEW.applicant_income + NEW.coapplicant_income) ELSE 0 END,
        has_coapplicant = NEW.coapplicant_income > 0,
        is_graduate = NEW.education = 'Graduate',
        is_self_employed = NEW.self_employed = 'Yes',
        has_credit_history = NEW.credit_history = 1,
        feature_created_at = NOW()
    WHERE loan_id = NEW.loan_id;
END //
DELIMITER ;

-- Trigger 5: Validate prediction data before insert
DELIMITER //
CREATE TRIGGER before_prediction_insert
BEFORE INSERT ON loan_predictions
FOR EACH ROW
BEGIN
    -- Validate confidence score
    IF NEW.confidence_score < 0 OR NEW.confidence_score > 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Confidence score must be between 0 and 1';
    END IF;
    
    -- Validate probability
    IF NEW.probability_approved < 0 OR NEW.probability_approved > 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Probability must be between 0 and 1';
    END IF;
    
    -- Check if loan application exists
    IF NOT EXISTS (SELECT 1 FROM loan_applications WHERE loan_id = NEW.loan_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan application does not exist';
    END IF;
END //
DELIMITER ;

-- Trigger 6: Log prediction changes
DELIMITER //
CREATE TRIGGER after_prediction_insert
AFTER INSERT ON loan_predictions
FOR EACH ROW
BEGIN
    -- Log prediction to audit table (if exists)
    INSERT INTO prediction_audit (
        prediction_id,
        loan_id,
        predicted_status,
        confidence_score,
        created_at
    ) VALUES (
        NEW.prediction_id,
        NEW.loan_id,
        NEW.predicted_status,
        NEW.confidence_score,
        NOW()
    );
END //
DELIMITER ;

-- Create audit tables for logging (optional)
CREATE TABLE IF NOT EXISTS loan_application_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id VARCHAR(20) NOT NULL,
    change_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_loan_status ENUM('Y', 'N'),
    new_loan_status ENUM('Y', 'N'),
    old_applicant_income DECIMAL(10,2),
    new_applicant_income DECIMAL(10,2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_loan_id (loan_id),
    INDEX idx_changed_at (changed_at)
);

CREATE TABLE IF NOT EXISTS prediction_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NOT NULL,
    loan_id VARCHAR(20) NOT NULL,
    predicted_status ENUM('Approved', 'Rejected') NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prediction_id (prediction_id),
    INDEX idx_loan_id (loan_id),
    INDEX idx_created_at (created_at)
); 