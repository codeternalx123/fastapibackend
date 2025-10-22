from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional, List, Dict, Any
from datetime import datetime, time, date

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    is_superuser: bool = False

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=72)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[constr(min_length=8, max_length=72)] = None

class UserIn(BaseModel):
    username: EmailStr  # Using email as username
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PasswordReset(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=72)

class UserFeatures(BaseModel):
    age: int
    bmi: float
    sleep_hours: float
    stress_score: float
    genetic_marker: int

class RunRequest(BaseModel):
    user_id: str
    features: UserFeatures

class PaymentCreate(BaseModel):
    amount: float
    currency: str
    payment_method: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaymentResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    payment_method: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None
    quantum_security_score: Optional[float] = None

    class Config:
        from_attributes = True
    days: int = Field(default=2, ge=1, le=14)
    fasting_window: Optional[Dict[str,str]] = None

class PlanItem(BaseModel):
    name: str
    key: str
    day: int
    slot: str
    value: float
    unit: str

class PlanResponse(BaseModel):
    energy: float
    plan: List[PlanItem]
    meta: Optional[Dict[str, Any]] = None

class ReportRequest(BaseModel):
    plan: List[PlanItem]
    meta: Optional[Dict[str, Any]] = None

class TreatmentSchedule(BaseModel):
    """Treatment schedule model"""
    treatments: List[Dict[str, Any]] = Field(
        ...,
        description="List of scheduled treatments"
    )

class SleepData(BaseModel):
    """Sleep data model"""
    sleep_records: List[Dict[str, time]] = Field(
        ...,
        description="List of sleep records with times"
    )

class EnergyReport(BaseModel):
    """Energy level report model"""
    timestamp: datetime = Field(
        ...,
        description="Time of energy level report"
    )
    energy_level: float = Field(
        ...,
        ge=0,
        le=10,
        description="Energy level on scale of 0-10"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about energy level"
    )

class NutritionRecommendation(BaseModel):
    """Nutrition recommendation model"""
    recommendation_date: date = Field(
        ...,
        description="Date of recommendation"
    )
    meal_timing: time = Field(
        ...,
        description="Recommended meal time"
    )
    foods: List[str] = Field(
        ...,
        description="List of recommended foods"
    )
    nutrients: List[str] = Field(
        ...,
        description="List of key nutrients to focus on"
    )
    hydration_target: float = Field(
        ...,
        ge=0,
        description="Daily hydration target in liters"
    )

class FastingWindow(BaseModel):
    """Fasting window model"""
    fasting_date: date = Field(
        ...,
        description="Date of fasting window"
    )
    start_time: time = Field(
        ...,
        description="Start time of fasting period"
    )
    end_time: time = Field(
        ...,
        description="End time of fasting period"
    )
    duration: float = Field(
        ...,
        ge=0,
        description="Duration of fasting in hours"
    )
    has_treatment: bool = Field(
        ...,
        description="Whether this window includes treatment"
    )

class FastingPlan(BaseModel):
    """Complete fasting plan model"""
    fasting_windows: List[Dict[str, Any]] = Field(
        ...,
        description="List of fasting windows"
    )
    nutrition_recommendations: List[NutritionRecommendation] = Field(
        ...,
        description="Nutrition recommendations for each window"
    )
    treatment_alignment_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Score for alignment with treatment schedule"
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Overall confidence score for the plan"
    )

class HealthProfileBase(BaseModel):
    """Base health profile model"""
    height: float = Field(..., description="Height in centimeters")
    weight: float = Field(..., description="Weight in kilograms")
    age: int = Field(..., description="Age in years")
    gender: str = Field(..., description="Gender")
    medical_conditions: List[str] = Field(default=[], description="List of medical conditions")
    allergies: List[str] = Field(default=[], description="List of allergies")
    medications: List[str] = Field(default=[], description="List of current medications")

class HealthProfileCreate(HealthProfileBase):
    """Create health profile model"""
    pass

class HealthProfileUpdate(HealthProfileBase):
    """Update health profile model"""
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class HealthProfileOut(HealthProfileBase):
    """Health profile output model"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HealthMetricCreate(BaseModel):
    """Create health metric model"""
    type: str = Field(..., description="Type of health metric")
    value: float = Field(..., description="Value of the metric")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthMetricOut(HealthMetricCreate):
    """Health metric output model"""
    id: int
    user_id: int

    class Config:
        from_attributes = True

class MetricsSummary(BaseModel):
    """Summary of health metrics"""
    metric_type: str
    average: float
    min_value: float
    max_value: float
    trend: str  # 'increasing', 'decreasing', or 'stable'
    period: str  # 'day', 'week', 'month'

class TreatmentEffectiveness(BaseModel):
    """Treatment effectiveness model"""
    plan_id: int
    effectiveness_score: float
    confidence_interval: List[float]
    key_factors: List[str]

class UserProgress(BaseModel):
    """User progress tracking model"""
    metric_name: str
    current_value: float
    baseline_value: float
    improvement_percentage: float
    time_period: str

class MetricsCorrelation(BaseModel):
    """Metrics correlation analysis"""
    metric1: str
    metric2: str
    correlation_coefficient: float
    p_value: float
    sample_size: int

class TrendAnalysis(BaseModel):
    """Trend analysis model"""
    metric: str
    trend_direction: str
    trend_strength: float
    seasonal_pattern: Optional[str] = None
    forecast_values: List[float]

class AnalyticsSummary(BaseModel):
    """Overall analytics summary"""
    user_id: int
    total_plans: int
    completed_plans: int
    average_optimization_score: float
    key_metrics: List[MetricsSummary]
    recent_trends: List[TrendAnalysis]
    effectiveness_analysis: List[TreatmentEffectiveness]

class CompoundInfo(BaseModel):
    """Molecular compound information"""
    name: str
    concentration: float
    confidence_score: float
    cancer_relation: Optional[Dict[str, Any]] = None
    treatment_interactions: Optional[Dict[str, Any]] = None

class FoodScanRequest(BaseModel):
    """Food scan request model"""
    scan_type: str = Field(..., description="Type of scan: 'camera' or 'hyperspectral'")
    user_state: Dict[str, Any] = Field(..., description="Current user health state information")
    scan_options: Optional[Dict[str, Any]] = None

class FoodScanResponse(BaseModel):
    """Food scan response model"""
    scan_id: int
    timestamp: datetime
    synergy_score: float
    compounds: List[CompoundInfo]
    nutritional_data: Dict[str, Any]
    cancer_markers: Dict[str, Any]
    warning_flags: List[str]
    analysis_metadata: Dict[str, Any]

class FoodRecommendationResponse(BaseModel):
    """Food recommendation response model"""
    recommendations: List[Dict[str, Any]]
    alternatives: Dict[str, List[str]]
    safety_notes: Optional[str] = None
    medical_references: Optional[List[Dict[str, str]]] = None

class CompoundAnalysisResponse(BaseModel):
    """Compound analysis response model"""
    compound_name: str
    chemical_formula: str
    molecular_weight: float
    cancer_relation: Dict[str, Any]
    treatment_interactions: Dict[str, Any]
    safety_data: Dict[str, Any]
    research_references: List[Dict[str, str]]

class FoodScanRequest(BaseModel):
    """Food scan request model"""
    scan_type: str = Field(..., description="Type of scan: 'camera' or 'hyperspectral'")
    user_state: Dict[str, Any] = Field(..., description="Current user health state information")
    scan_options: Optional[Dict[str, Any]] = None

class FoodScanResponse(BaseModel):
    """Food scan response model"""
    scan_id: int
    timestamp: datetime
    synergy_score: float
    compounds: List[CompoundInfo]
    nutritional_data: Dict[str, Any]
    cancer_markers: Dict[str, Any]
    warning_flags: List[str]
    analysis_metadata: Dict[str, Any]

class FoodRecommendationResponse(BaseModel):
    """Food recommendation response model"""
    recommendations: List[Dict[str, Any]]
    alternatives: Dict[str, List[str]]
    safety_notes: Optional[str] = None
    medical_references: Optional[List[Dict[str, str]]] = None
