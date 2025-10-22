from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.deps import get_current_user, get_db
from app.models.database import User, HealthProfile, HealthMetric, TreatmentPlan
from app.models.schemas import (
    HealthProfileCreate,
    HealthProfileUpdate,
    HealthProfileOut,
    HealthMetricCreate,
    HealthMetricOut,
    MetricsSummary
)

router = APIRouter()

@router.post("/profile", response_model=HealthProfileOut)
async def create_health_profile(
    profile: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_profile = HealthProfile(
        user_id=current_user.id,
        **profile.dict()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profile", response_model=HealthProfileOut)
async def get_health_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).order_by(HealthProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    return profile

@router.put("/profile", response_model=HealthProfileOut)
async def update_health_profile(
    profile: HealthProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).order_by(HealthProfile.created_at.desc()).first()
    
    if not db_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.post("/metrics", response_model=HealthMetricOut)
async def create_health_metric(
    metric: HealthMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).order_by(HealthProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    db_metric = HealthMetric(
        profile_id=profile.id,
        **metric.dict()
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).order_by(HealthProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(HealthMetric).filter(
        HealthMetric.profile_id == profile.id,
        HealthMetric.measured_at >= cutoff_date
    ).all()
    
    # Group metrics by type and calculate averages
    metrics_by_type = {}
    for metric in metrics:
        if metric.metric_type not in metrics_by_type:
            metrics_by_type[metric.metric_type] = []
        metrics_by_type[metric.metric_type].append(metric.value)
    
    summary = {
        metric_type: sum(values) / len(values)
        for metric_type, values in metrics_by_type.items()
    }
    
    return MetricsSummary(
        period_days=days,
        metrics=summary
    )

@router.get("/metrics/history", response_model=List[HealthMetricOut])
async def get_metrics_history(
    metric_type: str,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).order_by(HealthProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(HealthMetric).filter(
        HealthMetric.profile_id == profile.id,
        HealthMetric.metric_type == metric_type,
        HealthMetric.measured_at >= cutoff_date
    ).order_by(HealthMetric.measured_at.asc()).all()
    
    return metrics