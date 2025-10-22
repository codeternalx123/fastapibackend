from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.deps import get_current_user, get_db
from app.models.database import (
    User,
    HealthProfile,
    HealthMetric,
    TreatmentPlan,
    TreatmentPlanItem,
    PlanAnalytics
)
from app.models.schemas import (
    AnalyticsSummary,
    TreatmentEffectiveness,
    UserProgress,
    MetricsCorrelation,
    TrendAnalysis
)
import numpy as np
from scipy import stats

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall analytics summary for the user"""
    try:
        # Get latest health profile
        profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == current_user.id
        ).order_by(desc(HealthProfile.created_at)).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="No health profile found")
        
        # Get treatment plan statistics
        plans = db.query(TreatmentPlan).filter(
            TreatmentPlan.user_id == current_user.id
        ).all()
        
        total_plans = len(plans)
        completed_plans = sum(1 for p in plans if p.status == "completed")
        
        # Calculate average optimization score
        avg_score = (
            db.query(func.avg(TreatmentPlan.optimization_score))
            .filter(TreatmentPlan.user_id == current_user.id)
            .scalar() or 0.0
        )
        
        return {
            "total_plans": total_plans,
            "completed_plans": completed_plans,
            "completion_rate": completed_plans / total_plans if total_plans > 0 else 0,
            "average_optimization_score": avg_score,
            "current_stress_level": profile.stress_score,
            "current_sleep_quality": profile.sleep_hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/effectiveness", response_model=TreatmentEffectiveness)
async def analyze_treatment_effectiveness(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze the effectiveness of a specific treatment plan"""
    plan = db.query(TreatmentPlan).filter(
        TreatmentPlan.id == plan_id,
        TreatmentPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Get metrics before and after plan
    before_metrics = db.query(HealthMetric).filter(
        HealthMetric.measured_at < plan.start_date
    ).all()
    
    after_metrics = db.query(HealthMetric).filter(
        HealthMetric.measured_at > plan.end_date
    ).all()
    
    # Calculate changes in key metrics
    metric_changes = {}
    for metric_type in ["stress", "sleep", "inflammation"]:
        before_avg = np.mean([m.value for m in before_metrics if m.metric_type == metric_type]) if before_metrics else 0
        after_avg = np.mean([m.value for m in after_metrics if m.metric_type == metric_type]) if after_metrics else 0
        metric_changes[metric_type] = {
            "before": before_avg,
            "after": after_avg,
            "change": after_avg - before_avg
        }
    
    return {
        "plan_id": plan_id,
        "duration_days": (plan.end_date - plan.start_date).days,
        "completion_rate": sum(1 for item in plan.plan_items if item.completed) / len(plan.plan_items),
        "metric_changes": metric_changes,
        "optimization_score": plan.optimization_score
    }

@router.get("/progress", response_model=UserProgress)
async def track_user_progress(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track user's progress over time"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all metrics in time period
    metrics = db.query(HealthMetric).join(
        HealthProfile
    ).filter(
        HealthProfile.user_id == current_user.id,
        HealthMetric.measured_at >= cutoff_date
    ).all()
    
    # Group metrics by type and calculate trends
    metric_trends = {}
    for metric_type in set(m.metric_type for m in metrics):
        type_metrics = [m for m in metrics if m.metric_type == metric_type]
        values = [m.value for m in type_metrics]
        timestamps = [m.measured_at.timestamp() for m in type_metrics]
        
        if len(values) > 1:
            slope, _, r_value, _, _ = stats.linregress(timestamps, values)
            trend = "improving" if slope < 0 else "worsening" if slope > 0 else "stable"
            correlation = r_value
        else:
            trend = "insufficient_data"
            correlation = 0
            
        metric_trends[metric_type] = {
            "trend": trend,
            "correlation": correlation,
            "values": values
        }
    
    return {
        "period_days": days,
        "metric_trends": metric_trends,
        "total_measurements": len(metrics)
    }

@router.get("/correlations", response_model=MetricsCorrelation)
async def analyze_metric_correlations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze correlations between different health metrics"""
    metrics = db.query(HealthMetric).join(
        HealthProfile
    ).filter(
        HealthProfile.user_id == current_user.id
    ).all()
    
    # Group metrics by type
    metric_groups = {}
    for m in metrics:
        if m.metric_type not in metric_groups:
            metric_groups[m.metric_type] = []
        metric_groups[m.metric_type].append(m.value)
    
    # Calculate correlations between metrics
    correlations = {}
    for type1 in metric_groups:
        correlations[type1] = {}
        for type2 in metric_groups:
            if len(metric_groups[type1]) == len(metric_groups[type2]):
                correlation, _ = stats.pearsonr(metric_groups[type1], metric_groups[type2])
                correlations[type1][type2] = correlation
            else:
                correlations[type1][type2] = None
    
    return {
        "correlations": correlations,
        "sample_size": len(metrics),
        "metric_types": list(metric_groups.keys())
    }

@router.get("/trends", response_model=TrendAnalysis)
async def analyze_trends(
    metric_type: str,
    window_days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze trends for a specific metric type"""
    cutoff_date = datetime.utcnow() - timedelta(days=window_days)
    
    metrics = db.query(HealthMetric).join(
        HealthProfile
    ).filter(
        HealthProfile.user_id == current_user.id,
        HealthMetric.metric_type == metric_type,
        HealthMetric.measured_at >= cutoff_date
    ).order_by(HealthMetric.measured_at).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No {metric_type} metrics found")
    
    values = [m.value for m in metrics]
    timestamps = [m.measured_at.timestamp() for m in metrics]
    
    # Calculate basic statistics
    mean = np.mean(values)
    std = np.std(values)
    
    # Calculate trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
    
    # Detect anomalies (values outside 2 standard deviations)
    anomalies = [
        (m.measured_at.isoformat(), m.value)
        for m in metrics
        if abs(m.value - mean) > 2 * std
    ]
    
    return {
        "metric_type": metric_type,
        "window_days": window_days,
        "mean": mean,
        "std": std,
        "trend": {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "std_err": std_err
        },
        "anomalies": anomalies,
        "data_points": len(metrics)
    }