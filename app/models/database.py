from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.security import get_password_hash

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    health_profiles = relationship("HealthProfile", back_populates="user")
    treatment_plans = relationship("TreatmentPlan", back_populates="user")
    
    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

class HealthProfile(Base):
    __tablename__ = "health_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    sleep_hours = Column(Float)
    stress_score = Column(Float)
    genetic_marker = Column(Integer)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    medications = Column(JSON)
    allergies = Column(JSON)
    conditions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="health_profiles")
    metrics = relationship("HealthMetric", back_populates="health_profile")

class HealthMetric(Base):
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"))
    metric_type = Column(String)  # e.g., "blood_sugar", "inflammation_marker"
    value = Column(Float)
    unit = Column(String)
    measured_at = Column(DateTime(timezone=True))
    notes = Column(String)
    
    health_profile = relationship("HealthProfile", back_populates="metrics")

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String)  # active, completed, cancelled
    optimization_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="treatment_plans")
    plan_items = relationship("TreatmentPlanItem", back_populates="plan")
    analytics = relationship("PlanAnalytics", back_populates="plan")

class TreatmentPlanItem(Base):
    __tablename__ = "treatment_plan_items"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("treatment_plans.id"))
    name = Column(String)
    key = Column(String)
    day = Column(Integer)
    slot = Column(String)
    value = Column(Float)
    unit = Column(String)
    completed = Column(Boolean, default=False)
    completion_time = Column(DateTime(timezone=True))
    notes = Column(String)
    
    plan = relationship("TreatmentPlan", back_populates="plan_items")

class PlanAnalytics(Base):
    __tablename__ = "plan_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("treatment_plans.id"))
    metric_type = Column(String)  # e.g., "adherence", "effectiveness"
    value = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    plan = relationship("TreatmentPlan", back_populates="analytics")