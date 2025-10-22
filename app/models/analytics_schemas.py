from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class MetricSummary(BaseModel):
    """Statistical summary of a metric"""
    metric: str
    count: int
    mean: float
    std: float
    min: float
    q1: float
    median: float
    q3: float
    max: float
    skewness: float
    kurtosis: float
    missing_ratio: float

class TimeSeriesDecomposition(BaseModel):
    """Time series decomposition components"""
    trend: List[float]
    seasonal: List[float]
    residual: List[float]

class TrendAnalysis(BaseModel):
    """Trend analysis result"""
    metric: str
    direction: str
    strength: float
    seasonality_periods: List[int]
    change_points: List[int]
    decomposition: TimeSeriesDecomposition

class Correlation(BaseModel):
    """Correlation between two metrics"""
    metric1: str
    metric2: str
    coefficient: float
    pvalue: float
    relationship_type: str

class Forecast(BaseModel):
    """Forecast result for a metric"""
    metric: str
    values: List[float]
    confidence_intervals: Dict[str, List[float]]
    accuracy: Dict[str, float]

class Anomaly(BaseModel):
    """Detected anomaly in a metric"""
    metric: str
    timestamp: datetime
    value: float
    severity: float

class ClusterResult(BaseModel):
    """Clustering analysis result"""
    cluster_id: int
    metrics: Dict[str, Dict[str, float]]
    temporal_patterns: Dict[str, Any]
    characteristics: Dict[str, Any]

class FeatureImportance(BaseModel):
    """Feature importance analysis result"""
    target: str
    feature: str
    importance_score: float
    method: str

class AnalyticsResult(BaseModel):
    """Complete analytics result"""
    summary: List[MetricSummary]
    trends: List[TrendAnalysis]
    correlations: List[Correlation]
    forecasts: List[Forecast]
    anomalies: List[Anomaly]
    patterns: List[Dict[str, Any]]
    importance: List[FeatureImportance]