from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Compound(BaseModel):
    name: str
    concentration: float
    confidence: float
    cancer_relation: Optional[Dict[str, Any]] = None
    treatment_interactions: Optional[Dict[str, Any]] = None

class Warning(BaseModel):
    level: str
    type: str
    compound: str
    message: str

class Recommendation(BaseModel):
    type: str
    message: str
    items: Optional[List[str]] = None

class ConfidenceScores(BaseModel):
    overall_confidence: float
    compound_detection_confidence: float
    nutritional_analysis_confidence: float

class FoodScanRequest(BaseModel):
    scan_type: str = "camera"
    additional_context: Optional[Dict[str, Any]] = None

class FoodScanResponse(BaseModel):
    scan_id: int
    synergy_score: float = Field(..., ge=0, le=100)
    warnings: List[Warning]
    recommendations: List[Recommendation]
    detected_compounds: List[Compound]
    confidence_scores: ConfidenceScores

class CompoundAnalysisResponse(BaseModel):
    compounds: List[Compound]
    cancer_markers: Dict[str, Any]
    analysis_metadata: Dict[str, Any]
    warning_flags: List[str]

class FoodRecommendationResponse(BaseModel):
    recommendations: List[Recommendation]

class ScanHistory(BaseModel):
    id: int
    timestamp: datetime
    synergy_score: float
    warning_count: int
    compound_count: int

class HistoricalAnalysis(BaseModel):
    scans: List[ScanHistory]
    average_synergy_score: float
    common_warnings: List[str]
    improvement_suggestions: List[str]