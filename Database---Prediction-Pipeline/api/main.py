
import os
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, date
import pandas as pd
import joblib
import numpy as np
import json

# Import local modules
from .database import (
    get_mysql_connection, 
    get_mongodb_db, 
    MySQLRepository, 
    MongoDBRepository,
    check_all_databases,
    get_db,
    create_tables,
    get_mongo_collections,
    LoanApplication,
    LoanPrediction,
    LoanAnalytics,
    LoanFeature  
)
from .models import (
    LoanApplicationCreate, LoanApplicationResponse, LoanApplicationUpdate,
    LoanPredictionCreate, LoanPredictionResponse, PredictionSearchParams,
    LoanStatistics, LoanAnalyticsResponse,
    LoanSearchParams, LoanFeaturesResponse,
    StandardResponse, PaginatedResponse,
    PredictionRequest, PredictionResponse,
    PredictedStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Loan Prediction API",
    description="API for loan prediction using machine learning with MySQL and MongoDB",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=StandardResponse(
            success=False,
            message="Internal server error",
            data={"detail": str(exc), "path": request.url.path}
        ).dict()
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Check the health status of the API and databases"""
    try:
        db_health = check_all_databases()
        return StandardResponse(
            success=True,
            message="Health check completed",
            data={
                "status": db_health["overall_status"],
                "mysql": db_health["mysql"],
                "mongodb": db_health["mongodb"]
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return StandardResponse(
            success=False,
            message="Health check failed",
            data={
                "status": "unhealthy",
                "mysql": {"status": "unknown"},
                "mongodb": {"status": "unknown"}
            }
        )

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return StandardResponse(
        success=True,
        message="Loan Prediction API",
        data={
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    )

# Loan Prediction Endpoints

@app.get("/loans/", response_model=List[LoanApplicationResponse])
def get_loan_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all loan applications with pagination"""
    loans = db.query(LoanApplication).offset(skip).limit(limit).all()
    return [LoanApplicationResponse.from_orm(loan) for loan in loans]

@app.get("/loans/search/", response_model=List[LoanApplicationResponse])
def search_loan_applications(
    params: LoanSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """Search loan applications with filters"""
    query = db.query(LoanApplication)
    
    if params.gender:
        query = query.filter(LoanApplication.gender == params.gender)
    if params.education:
        query = query.filter(LoanApplication.education == params.education)
    if params.property_area:
        query = query.filter(LoanApplication.property_area == params.property_area)
    if params.loan_status:
        query = query.filter(LoanApplication.loan_status == params.loan_status)
    if params.min_income is not None:
        query = query.filter(LoanApplication.applicant_income >= params.min_income)
    if params.max_income is not None:
        query = query.filter(LoanApplication.applicant_income <= params.max_income)
    
    loans = query.offset(params.offset).limit(params.limit).all()
    return [LoanApplicationResponse.from_orm(loan) for loan in loans]

@app.get("/loans/{loan_id}", response_model=LoanApplicationResponse)
def get_loan_application(loan_id: str, db: Session = Depends(get_db)):
    """Get a specific loan application by loan ID"""
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return LoanApplicationResponse.from_orm(loan)

@app.get("/loans/by-loan-id/{loan_id}", response_model=LoanApplicationResponse)
def get_loan_application_by_loan_id(loan_id: str, db: Session = Depends(get_db)):
    """Get a specific loan application by loan ID"""
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return LoanApplicationResponse.from_orm(loan)

@app.post("/loans/", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_loan_application(loan: LoanApplicationCreate, db: Session = Depends(get_db)):
    """Create a new loan application"""
    # Check if loan_id already exists
    existing_loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan.loan_id).first()
    if existing_loan:
        raise HTTPException(status_code=400, detail="Loan ID already exists")
    
    db_loan = LoanApplication(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return LoanApplicationResponse.from_orm(db_loan)

@app.put("/loans/{loan_id}", response_model=LoanApplicationResponse)
def update_loan_application(loan_id: str, loan: LoanApplicationUpdate, db: Session = Depends(get_db)):
    """Update a loan application"""
    db_loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    update_data = loan.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_loan, field, value)
    
    db.commit()
    db.refresh(db_loan)
    return LoanApplicationResponse.from_orm(db_loan)

@app.delete("/loans/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan_application(loan_id: str, db: Session = Depends(get_db)):
    """Delete a loan application"""
    db_loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    db.delete(db_loan)
    db.commit()
    return None

@app.get("/loans/{loan_id}/features", response_model=List[LoanFeaturesResponse])
def get_loan_features(loan_id: str, db: Session = Depends(get_db)):
    """Get features for a specific loan application"""
    features = db.query(LoanFeature).filter(LoanFeature.loan_application_id == loan_id).all()
    return [LoanFeaturesResponse.from_orm(f) for f in features]

@app.post("/loans/predict/", response_model=LoanPredictionResponse)
def predict_loan_approval(request: PredictionRequest, db: Session = Depends(get_db)):
    """Predict loan approval for a new application"""
    try:
        # Load the trained model (you would need to train this first)
        model_path = "ml/loan_prediction_model.pkl"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail="Loan prediction model not found. Please train the model first.")
        
        model = joblib.load(model_path)
        
        # Prepare features for prediction
        features = prepare_loan_features(request)
        
        # Make prediction
        prediction = model.predict([features])[0]
        confidence = model.predict_proba([features])[0].max()
        
        # Get feature importance if available
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_names = [
                'gender_male', 'married_yes', 'education_graduate', 'self_employed_yes',
                'credit_history_yes', 'dependents_count', 'property_area_encoded',
                'applicant_income', 'coapplicant_income', 'loan_amount', 'loan_amount_term',
                'total_income', 'income_to_loan_ratio', 'monthly_payment'
            ]
            feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        return LoanPredictionResponse(
            predicted_status=PredictedStatus.APPROVED if prediction == 1 else PredictedStatus.REJECTED,
            confidence_score=float(confidence),
            probability_approved=float(confidence) if prediction == 1 else 1.0 - float(confidence),
            feature_importance=feature_importance,
            model_version="1.0.0",
            prediction_id=0,  # This would be set when saved to database
            loan_id="",  # This would be set when saved to database
            prediction_created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def prepare_loan_features(request: PredictionRequest) -> List[float]:
    """Prepare loan features for ML prediction"""
    features = []
    
    # Categorical features (encoded)
    features.append(1 if request.gender == "Male" else 0)
    features.append(1 if request.married == "Yes" else 0)
    features.append(1 if request.education == "Graduate" else 0)
    features.append(1 if request.self_employed == "Yes" else 0)
    features.append(request.credit_history if request.credit_history is not None else 0)
    
    # Dependents (encoded)
    dependents_map = {"0": 0, "1": 1, "2": 2, "3+": 3}
    dependents_count = dependents_map.get(request.dependents, 0) if request.dependents else 0
    features.append(dependents_count)
    
    # Property area (encoded)
    property_map = {"Urban": 0, "Semiurban": 1, "Rural": 2}
    property_encoded = property_map.get(request.property_area, 0) if request.property_area else 0
    features.append(property_encoded)
    
    # Numerical features
    features.append(request.applicant_income)
    features.append(request.coapplicant_income)
    features.append(request.loan_amount if request.loan_amount else 0)
    features.append(request.loan_amount_term if request.loan_amount_term else 360)
    
    # Derived features
    total_income = request.applicant_income + request.coapplicant_income
    features.append(total_income)
    
    income_to_loan_ratio = total_income / request.loan_amount if request.loan_amount and request.loan_amount > 0 else 0
    features.append(income_to_loan_ratio)
    
    monthly_payment = request.loan_amount / request.loan_amount_term if request.loan_amount and request.loan_amount_term else 0
    features.append(monthly_payment)
    
    return features

@app.post("/loans/{loan_id}/predict", response_model=LoanPredictionResponse)
def predict_existing_loan(loan_id: str, db: Session = Depends(get_db)):
    """Predict loan approval for an existing application"""
    # Get the loan application
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    try:
        # Load the trained model
        model_path = "ml/loan_prediction_model.pkl"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail="Loan prediction model not found. Please train the model first.")
        
        model = joblib.load(model_path)
        
        # Prepare features using Pydantic model
        request = PredictionRequest.parse_obj(LoanApplicationResponse.from_orm(loan).dict())
        features = prepare_loan_features(request)
        
        # Make prediction
        prediction = model.predict([features])[0]
        confidence = model.predict_proba([features])[0].max()
        
        # Get feature importance
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_names = [
                'gender_male', 'married_yes', 'education_graduate', 'self_employed_yes',
                'credit_history_yes', 'dependents_count', 'property_area_encoded',
                'applicant_income', 'coapplicant_income', 'loan_amount', 'loan_amount_term',
                'total_income', 'income_to_loan_ratio', 'monthly_payment'
            ]
            feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        # Save prediction to database
        db_prediction = LoanPrediction(
            loan_application_id=loan_id,
            predicted_status="Y" if prediction == 1 else "N",
            confidence_score=float(confidence),
            model_version="1.0.0",
            feature_importance=feature_importance
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return LoanPredictionResponse.from_orm(db_prediction)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/loans/{loan_id}/predictions", response_model=List[LoanPredictionResponse])
def get_loan_predictions(loan_id: str, db: Session = Depends(get_db)):
    """Get all predictions for a specific loan application"""
    predictions = db.query(LoanPrediction).filter(LoanPrediction.loan_application_id == loan_id).all()
    return [LoanPredictionResponse.from_orm(p) for p in predictions]

@app.get("/loans/statistics/overview")
def get_loan_statistics_overview(db: Session = Depends(get_db)):
    """Get overview statistics for loan applications"""
    try:
        # Total applications
        total_applications = db.query(func.count(LoanApplication.id)).scalar()
        
        # Approved vs rejected
        approved_loans = db.query(func.count(LoanApplication.id)).filter(LoanApplication.loan_status == "Y").scalar()
        rejected_loans = db.query(func.count(LoanApplication.id)).filter(LoanApplication.loan_status == "N").scalar()
        
        # Approval rate
        approval_rate = (approved_loans / total_applications * 100) if total_applications > 0 else 0
        
        # Average values
        avg_loan_amount = db.query(func.avg(LoanApplication.loan_amount)).scalar()
        avg_applicant_income = db.query(func.avg(LoanApplication.applicant_income)).scalar()
        avg_coapplicant_income = db.query(func.avg(LoanApplication.coapplicant_income)).scalar()
        
        # Gender distribution
        gender_stats = db.query(
            LoanApplication.gender,
            func.count(LoanApplication.id).label('count')
        ).filter(LoanApplication.gender.isnot(None)).group_by(LoanApplication.gender).all()
        
        # Education distribution
        education_stats = db.query(
            LoanApplication.education,
            func.count(LoanApplication.id).label('count')
        ).filter(LoanApplication.education.isnot(None)).group_by(LoanApplication.education).all()
        
        # Property area distribution
        property_stats = db.query(
            LoanApplication.property_area,
            func.count(LoanApplication.id).label('count')
        ).filter(LoanApplication.property_area.isnot(None)).group_by(LoanApplication.property_area).all()
        
        return StandardResponse(
            success=True,
            message="Loan statistics retrieved successfully",
            data={
                "total_applications": total_applications,
                "approved_loans": approved_loans,
                "rejected_loans": rejected_loans,
                "approval_rate": round(approval_rate, 2),
                "avg_loan_amount": float(avg_loan_amount) if avg_loan_amount else 0,
                "avg_applicant_income": float(avg_applicant_income) if avg_applicant_income else 0,
                "avg_coapplicant_income": float(avg_coapplicant_income) if avg_coapplicant_income else 0,
                "gender_distribution": {stat.gender: stat.count for stat in gender_stats},
                "education_distribution": {stat.education: stat.count for stat in education_stats},
                "property_area_distribution": {stat.property_area: stat.count for stat in property_stats}
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")

# MongoDB endpoints
@app.get("/mongodb/loans", tags=["MongoDB"])
async def get_mongodb_loans(
    limit: int = Query(100, ge=1, le=1000),
    loan_status: Optional[str] = Query(None)
):
    """Get loan documents from MongoDB"""
    try:
        db = get_mongodb_db()
        repo = MongoDBRepository(db)
        
        filter_dict = {}
        if loan_status:
            filter_dict["loan_status"] = loan_status
        
        results = repo.find_many("loan_documents", filter_dict, limit)
        return StandardResponse(
            success=True,
            message="MongoDB loans retrieved successfully",
            data={"loans": results, "count": len(results)}
        )
    except Exception as e:
        logger.error(f"Error getting MongoDB loans: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MongoDB loans")

@app.get("/mongodb/predictions", tags=["MongoDB"])
async def get_mongodb_predictions(
    loan_id: Optional[str] = Query(None),
    model_version: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get prediction results from MongoDB"""
    try:
        db = get_mongodb_db()
        repo = MongoDBRepository(db)
        
        filter_dict = {}
        if loan_id:
            filter_dict["loan_id"] = loan_id
        if model_version:
            filter_dict["model_version"] = model_version
        
        results = repo.find_many("prediction_results", filter_dict, limit)
        return StandardResponse(
            success=True,
            message="MongoDB predictions retrieved successfully",
            data={"predictions": results, "count": len(results)}
        )
    except Exception as e:
        logger.error(f"Error getting MongoDB predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve MongoDB predictions")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 