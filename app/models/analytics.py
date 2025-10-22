from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class AnalyticsSummary(BaseModel):
    total_plans: int
    completed_plans: int
    completion_rate: float
    average_optimization_score: float
    current_stress_level: float
    current_sleep_quality: float

class MetricChange(BaseModel):
    before: float
    after: float
    change: float

class TreatmentEffectiveness(BaseModel):
    plan_id: int
    duration_days: int
    completion_rate: float
    metric_changes: Dict[str, MetricChange]
    optimization_score: float

class MetricTrend(BaseModel):
    trend: str  # "improving", "worsening", "stable", "insufficient_data"
    correlation: float
    values: List[float]

class UserProgress(BaseModel):
    period_days: int
    metric_trends: Dict[str, MetricTrend]
    total_measurements: int

class MetricsCorrelation(BaseModel):
    correlations: Dict[str, Dict[str, Optional[float]]]
    sample_size: int
    metric_types: List[str]

class TrendStats(BaseModel):
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_err: float

class TrendAnalysis(BaseModel):
    metric_type: str
    window_days: int
    mean: float
    std: float
    trend: TrendStats
    anomalies: List[tuple[str, float]]  # [(timestamp, value), ...]
    data_points: int