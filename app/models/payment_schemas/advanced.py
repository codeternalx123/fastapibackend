from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TumorAnalysisRequest(BaseModel):
    """Request model for tumor analysis"""
    genomic_data: Dict[str, Any] = Field(
        ...,
        description="Genomic sequencing data including mutations and expressions"
    )
    biopsy_results: Dict[str, Any] = Field(
        ...,
        description="Results from tumor biopsy including histology"
    )
    blood_panel: Dict[str, Any] = Field(
        ...,
        description="Comprehensive blood panel results"
    )

class TumorAnalysisResponse(BaseModel):
    """Response model for tumor analysis results"""
    analysis_id: str = Field(..., description="Unique identifier for analysis")
    tumor_profile: Dict[str, Any] = Field(
        ...,
        description="Detailed tumor characterization"
    )
    vulnerabilities: List[Dict[str, Any]] = Field(
        ...,
        description="Identified tumor vulnerabilities"
    )
    recommended_interventions: List[Dict[str, Any]] = Field(
        ...,
        description="Recommended therapeutic targets"
    )
    confidence_score: float = Field(
        ...,
        description="Analysis confidence score (0-1)",
        ge=0,
        le=1
    )

class MetricType(str, Enum):
    """Types of body metrics"""
    INFLAMMATION = "inflammation"
    STRESS = "stress"
    SLEEP = "sleep"
    TUMOR = "tumor"
    IMMUNE = "immune"
    METABOLIC = "metabolic"

class BodyMetrics(BaseModel):
    """Model for body metrics"""
    scan_id: int
    inflammation_level: float = Field(..., ge=0, le=100)
    stress_level: float = Field(..., ge=0, le=100)
    sleep_quality: float = Field(..., ge=0, le=100)
    tumor_metrics: Dict[str, float]
    immune_markers: Dict[str, float]
    metabolic_markers: Dict[str, float]
    timestamp: datetime

class BodyScanResponse(BaseModel):
    """Response model for body scan results"""
    scan_id: int
    metrics: Dict[MetricType, Any]
    timestamp: datetime

class Recommendation(BaseModel):
    """Model for lifestyle recommendations"""
    category: str
    priority: int = Field(..., ge=1, le=5)
    description: str
    expected_impact: float = Field(..., ge=0, le=100)
    time_to_impact: str
    scientific_basis: str
    contraindications: Optional[List[str]] = None

class LifestyleRecommendations(BaseModel):
    """Response model for lifestyle optimization"""
    diet: List[Recommendation]
    exercise: List[Recommendation]
    stress_management: List[Recommendation]
    sleep: List[Recommendation]
    supplements: List[Recommendation]
    environmental: List[Recommendation]
    treatment_synergy: List[Recommendation]
    timestamp: datetime

class CancerProgressionScore(BaseModel):
    """Model for Cancer Progression Potential Score"""
    cpps: float = Field(
        ...,
        description="Cancer Progression Potential Score (0-100)",
        ge=0,
        le=100
    )
    interpretation: str
    recommendations: Dict[str, float]  # Intervention -> Expected Impact
    timestamp: datetime