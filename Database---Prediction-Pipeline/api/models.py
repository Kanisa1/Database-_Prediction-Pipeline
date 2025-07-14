from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for validation
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class Married(str, Enum):
    YES = "Yes"
    NO = "No"

class Dependents(str, Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE_PLUS = "3+"

class Education(str, Enum):
    GRADUATE = "Graduate"
    NOT_GRADUATE = "Not Graduate"

class SelfEmployed(str, Enum):
    YES = "Yes"
    NO = "No"

class PropertyArea(str, Enum):
    URBAN = "Urban"
    SEMIURBAN = "Semiurban"
    RURAL = "Rural"

class LoanStatus(str, Enum):
    APPROVED = "Y"
    REJECTED = "N"

class PredictedStatus(str, Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"

# Base Models
class LoanApplicationBase(BaseModel):
    gender: Gender
    married: Married
    dependents: Dependents
    education: Education
    self_employed: SelfEmployed
    applicant_income: float = Field(..., gt=0, description="Applicant's income")
    coapplicant_income: float = Field(..., ge=0, description="Co-applicant's income")
    loan_amount: Optional[float] = Field(None, ge=0, description="Loan amount requested")
    loan_amount_term: Optional[int] = Field(None, gt=0, description="Loan term in months")
    credit_history: Optional[int] = Field(None, ge=0, le=1, description="Credit history (0 or 1)")
    property_area: PropertyArea
    loan_status: Optional[LoanStatus] = None

class LoanApplicationCreate(LoanApplicationBase):
    loan_id: str = Field(..., min_length=1, max_length=20, description="Unique loan ID")

class LoanApplicationUpdate(BaseModel):
    applicant_income: Optional[float] = Field(None, gt=0)
    coapplicant_income: Optional[float] = Field(None, ge=0)
    loan_amount: Optional[float] = Field(None, ge=0)
    loan_status: Optional[LoanStatus] = None

class LoanApplicationResponse(LoanApplicationBase):
    loan_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

# Feature Models
class LoanFeaturesBase(BaseModel):
    total_income: float = Field(..., gt=0)
    income_ratio: Optional[float] = None
    loan_to_income_ratio: Optional[float] = None
    has_coapplicant: bool = False
    is_graduate: bool = False
    is_self_employed: bool = False
    has_credit_history: bool = False

class LoanFeaturesResponse(LoanFeaturesBase):
    feature_id: int
    loan_id: str
    feature_created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

# Prediction Models
class LoanPredictionBase(BaseModel):
    predicted_status: PredictedStatus
    confidence_score: float = Field(..., ge=0, le=1)
    probability_approved: float = Field(..., ge=0, le=1)
    model_version: str = "v1.0"

class LoanPredictionCreate(LoanPredictionBase):
    loan_id: str

class LoanPredictionResponse(LoanPredictionBase):
    prediction_id: int
    loan_id: str
    prediction_created_at: Optional[datetime] = None
    feature_importance: Optional[Dict[str, float]] = None

    class Config:
        orm_mode = True
        from_attributes = True

# Analytics Models
class LoanAnalyticsBase(BaseModel):
    total_applications: int = Field(..., ge=0)
    approved_loans: int = Field(..., ge=0)
    rejected_loans: int = Field(..., ge=0)
    approval_rate: float = Field(..., ge=0, le=100)
    avg_applicant_income: float = Field(..., gt=0)
    avg_loan_amount: float = Field(..., gt=0)

class LoanAnalyticsResponse(LoanAnalyticsBase):
    analytics_id: int
    analysis_date: datetime
    gender_distribution: Optional[Dict[str, int]] = None
    education_distribution: Optional[Dict[str, int]] = None
    property_area_distribution: Optional[Dict[str, int]] = None
    analytics_created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Search and Filter Models
class LoanSearchParams(BaseModel):
    gender: Optional[Gender] = None
    education: Optional[Education] = None
    property_area: Optional[PropertyArea] = None
    loan_status: Optional[LoanStatus] = None
    min_income: Optional[float] = Field(None, gt=0)
    max_income: Optional[float] = Field(None, gt=0)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

class PredictionSearchParams(BaseModel):
    predicted_status: Optional[PredictedStatus] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    max_confidence: Optional[float] = Field(None, ge=0, le=1)
    model_version: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Response Models
class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class LoanStatistics(BaseModel):
    total_applications: int
    approved_loans: int
    rejected_loans: int
    approval_rate: float
    avg_applicant_income: float
    avg_loan_amount: float
    gender_distribution: Dict[str, int]
    education_distribution: Dict[str, int]
    property_area_distribution: Dict[str, int]

# ML Prediction Models
class PredictionRequest(BaseModel):
    gender: Gender
    married: Married
    dependents: Dependents
    education: Education
    self_employed: SelfEmployed
    applicant_income: float = Field(..., gt=0)
    coapplicant_income: float = Field(..., ge=0)
    loan_amount: Optional[float] = Field(None, ge=0)
    loan_amount_term: Optional[int] = Field(None, gt=0)
    credit_history: Optional[int] = Field(None, ge=0, le=1)
    property_area: PropertyArea

class PredictionResponse(BaseModel):
    predicted_status: PredictedStatus
    confidence_score: float
    probability_approved: float
    feature_importance: Dict[str, float]
    model_version: str
    prediction_timestamp: datetime 