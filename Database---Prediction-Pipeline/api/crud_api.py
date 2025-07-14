from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean, Enum, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date
import os

# SQLAlchemy setup
MYSQL_URL = (
    f"mysql+mysqlconnector://{os.getenv('MYSQL_USER', 'root')}:"
    f"{os.getenv('MYSQL_PASSWORD', 'Kanisa')}@{os.getenv('MYSQL_HOST', 'localhost')}:"
    f"{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'loan_prediction_db')}"
)
engine = create_engine(MYSQL_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Models ---
class LoanApplication(Base):
    __tablename__ = "loan_applications"
    loan_id = Column(String(20), primary_key=True, index=True)
    gender = Column(Enum('Male', 'Female'), nullable=False)
    married = Column(Enum('Yes', 'No'), nullable=False)
    dependents = Column(Enum('0', '1', '2', '3+'), nullable=False)
    education = Column(Enum('Graduate', 'Not Graduate'), nullable=False)
    self_employed = Column(Enum('Yes', 'No'), nullable=False)
    applicant_income = Column(DECIMAL(10, 2), nullable=False)
    coapplicant_income = Column(DECIMAL(10, 2), nullable=False)
    loan_amount = Column(DECIMAL(10, 2), nullable=True)
    loan_amount_term = Column(Integer, nullable=True)
    credit_history = Column(Integer, nullable=True)
    property_area = Column(Enum('Urban', 'Semiurban', 'Rural'), nullable=False)
    loan_status = Column(Enum('Y', 'N'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class LoanFeature(Base):
    __tablename__ = "loan_features"
    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), nullable=False)
    total_income = Column(DECIMAL(10, 2), nullable=False)
    income_ratio = Column(DECIMAL(5, 2), nullable=True)
    has_coapplicant = Column(Boolean, default=False)
    is_graduate = Column(Boolean, default=False)
    is_self_employed = Column(Boolean, default=False)
    has_credit_history = Column(Boolean, default=False)
    feature_created_at = Column(DateTime, default=datetime.now)

class LoanPrediction(Base):
    __tablename__ = "loan_predictions"
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(String(20), nullable=False)
    predicted_status = Column(Enum('Approved', 'Rejected'), nullable=False)
    confidence_score = Column(DECIMAL(5, 4), nullable=False)
    probability_approved = Column(DECIMAL(5, 4), nullable=False)
    model_version = Column(String(20), default='v1.0')
    prediction_created_at = Column(DateTime, default=datetime.now)

class LoanAnalytics(Base):
    __tablename__ = "loan_analytics"
    analytics_id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date, nullable=False)
    total_applications = Column(Integer, nullable=False)
    approved_loans = Column(Integer, nullable=False)
    rejected_loans = Column(Integer, nullable=False)
    approval_rate = Column(DECIMAL(5, 2), nullable=False)
    avg_applicant_income = Column(DECIMAL(10, 2), nullable=False)
    avg_loan_amount = Column(DECIMAL(10, 2), nullable=False)
    analytics_created_at = Column(DateTime, default=datetime.now)

# --- Pydantic Schemas ---
class LoanApplicationBase(BaseModel):
    loan_id: str
    gender: str
    married: str
    dependents: str
    education: str
    self_employed: str
    applicant_income: float
    coapplicant_income: float
    loan_amount: Optional[float] = None
    loan_amount_term: Optional[int] = None
    credit_history: Optional[int] = None
    property_area: str
    loan_status: str

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationUpdate(BaseModel):
    gender: Optional[str]
    married: Optional[str]
    dependents: Optional[str]
    education: Optional[str]
    self_employed: Optional[str]
    applicant_income: Optional[float]
    coapplicant_income: Optional[float]
    loan_amount: Optional[float]
    loan_amount_term: Optional[int]
    credit_history: Optional[int]
    property_area: Optional[str]
    loan_status: Optional[str]

class LoanApplicationOut(LoanApplicationBase):
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class LoanFeatureBase(BaseModel):
    loan_id: str
    total_income: float
    income_ratio: Optional[float] = None
    has_coapplicant: bool
    is_graduate: bool
    is_self_employed: bool
    has_credit_history: bool

class LoanFeatureCreate(LoanFeatureBase):
    pass

class LoanFeatureUpdate(BaseModel):
    total_income: Optional[float]
    income_ratio: Optional[float]
    has_coapplicant: Optional[bool]
    is_graduate: Optional[bool]
    is_self_employed: Optional[bool]
    has_credit_history: Optional[bool]

class LoanFeatureOut(LoanFeatureBase):
    feature_id: int
    feature_created_at: datetime
    class Config:
        orm_mode = True

class LoanPredictionBase(BaseModel):
    loan_id: str
    predicted_status: str
    confidence_score: float
    probability_approved: float
    model_version: str

class LoanPredictionCreate(LoanPredictionBase):
    pass

class LoanPredictionUpdate(BaseModel):
    predicted_status: Optional[str]
    confidence_score: Optional[float]
    probability_approved: Optional[float]
    model_version: Optional[str]

class LoanPredictionOut(LoanPredictionBase):
    prediction_id: int
    prediction_created_at: datetime
    class Config:
        orm_mode = True

class LoanAnalyticsBase(BaseModel):
    analysis_date: date
    total_applications: int
    approved_loans: int
    rejected_loans: int
    approval_rate: float
    avg_applicant_income: float
    avg_loan_amount: float

class LoanAnalyticsCreate(LoanAnalyticsBase):
    pass

class LoanAnalyticsUpdate(BaseModel):
    total_applications: Optional[int]
    approved_loans: Optional[int]
    rejected_loans: Optional[int]
    approval_rate: Optional[float]
    avg_applicant_income: Optional[float]
    avg_loan_amount: Optional[float]

class LoanAnalyticsOut(LoanAnalyticsBase):
    analytics_id: int
    analytics_created_at: datetime
    class Config:
        orm_mode = True

# --- FastAPI App ---
app = FastAPI(title="Loan Prediction CRUD API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD Endpoints for loan_applications ---
@app.post("/loans/", response_model=LoanApplicationOut)
def create_loan_app(loan: LoanApplicationCreate, db: Session = Depends(get_db)):
    db_loan = LoanApplication(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

@app.get("/loans/", response_model=List[LoanApplicationOut])
def list_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LoanApplication).offset(skip).limit(limit).all()

@app.get("/loans/{loan_id}", response_model=LoanApplicationOut)
def get_loan(loan_id: str, db: Session = Depends(get_db)):
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

@app.put("/loans/{loan_id}", response_model=LoanApplicationOut)
def update_loan(loan_id: str, update: LoanApplicationUpdate, db: Session = Depends(get_db)):
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(loan, k, v)
    db.commit()
    db.refresh(loan)
    return loan

@app.delete("/loans/{loan_id}")
def delete_loan(loan_id: str, db: Session = Depends(get_db)):
    loan = db.query(LoanApplication).filter(LoanApplication.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return {"detail": "Deleted"}

# --- CRUD Endpoints for loan_features ---
@app.post("/features/", response_model=LoanFeatureOut)
def create_feature(feature: LoanFeatureCreate, db: Session = Depends(get_db)):
    db_feature = LoanFeature(**feature.dict())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@app.get("/features/", response_model=List[LoanFeatureOut])
def list_features(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LoanFeature).offset(skip).limit(limit).all()

@app.get("/features/{feature_id}", response_model=LoanFeatureOut)
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(LoanFeature).filter(LoanFeature.feature_id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature

@app.put("/features/{feature_id}", response_model=LoanFeatureOut)
def update_feature(feature_id: int, update: LoanFeatureUpdate, db: Session = Depends(get_db)):
    feature = db.query(LoanFeature).filter(LoanFeature.feature_id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(feature, k, v)
    db.commit()
    db.refresh(feature)
    return feature

@app.delete("/features/{feature_id}")
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(LoanFeature).filter(LoanFeature.feature_id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    db.delete(feature)
    db.commit()
    return {"detail": "Deleted"}

# --- CRUD Endpoints for loan_predictions ---
@app.post("/predictions/", response_model=LoanPredictionOut)
def create_prediction(pred: LoanPredictionCreate, db: Session = Depends(get_db)):
    db_pred = LoanPrediction(**pred.dict())
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred

@app.get("/predictions/", response_model=List[LoanPredictionOut])
def list_predictions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LoanPrediction).offset(skip).limit(limit).all()

@app.get("/predictions/{prediction_id}", response_model=LoanPredictionOut)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    pred = db.query(LoanPrediction).filter(LoanPrediction.prediction_id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return pred

@app.put("/predictions/{prediction_id}", response_model=LoanPredictionOut)
def update_prediction(prediction_id: int, update: LoanPredictionUpdate, db: Session = Depends(get_db)):
    pred = db.query(LoanPrediction).filter(LoanPrediction.prediction_id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(pred, k, v)
    db.commit()
    db.refresh(pred)
    return pred

@app.delete("/predictions/{prediction_id}")
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    pred = db.query(LoanPrediction).filter(LoanPrediction.prediction_id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(pred)
    db.commit()
    return {"detail": "Deleted"}

# --- CRUD Endpoints for loan_analytics ---
@app.post("/analytics/", response_model=LoanAnalyticsOut)
def create_analytics(ana: LoanAnalyticsCreate, db: Session = Depends(get_db)):
    db_ana = LoanAnalytics(**ana.dict())
    db.add(db_ana)
    db.commit()
    db.refresh(db_ana)
    return db_ana

@app.get("/analytics/", response_model=List[LoanAnalyticsOut])
def list_analytics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LoanAnalytics).offset(skip).limit(limit).all()

@app.get("/analytics/{analytics_id}", response_model=LoanAnalyticsOut)
def get_analytics(analytics_id: int, db: Session = Depends(get_db)):
    ana = db.query(LoanAnalytics).filter(LoanAnalytics.analytics_id == analytics_id).first()
    if not ana:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return ana

@app.put("/analytics/{analytics_id}", response_model=LoanAnalyticsOut)
def update_analytics(analytics_id: int, update: LoanAnalyticsUpdate, db: Session = Depends(get_db)):
    ana = db.query(LoanAnalytics).filter(LoanAnalytics.analytics_id == analytics_id).first()
    if not ana:
        raise HTTPException(status_code=404, detail="Analytics not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(ana, k, v)
    db.commit()
    db.refresh(ana)
    return ana

@app.delete("/analytics/{analytics_id}")
def delete_analytics(analytics_id: int, db: Session = Depends(get_db)):
    ana = db.query(LoanAnalytics).filter(LoanAnalytics.analytics_id == analytics_id).first()
    if not ana:
        raise HTTPException(status_code=404, detail="Analytics not found")
    db.delete(ana)
    db.commit()
    return {"detail": "Deleted"} 