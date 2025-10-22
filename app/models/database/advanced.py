from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class AdvancedScan(Base):
    """Model for storing advanced food scan results"""
    __tablename__ = "advanced_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scan_data = Column(JSON)
    scan_results = Column(JSON)
    model_accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="advanced_scans")

class TumorAnalysis(Base):
    """Model for storing tumor analysis results"""
    __tablename__ = "tumor_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    genomic_data = Column(JSON)
    biopsy_results = Column(JSON)
    blood_panel = Column(JSON)
    tumor_profile = Column(JSON)
    vulnerabilities = Column(JSON)
    recommended_interventions = Column(JSON)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tumor_analyses")

class BodyScan(Base):
    """Model for storing body scan results"""
    __tablename__ = "body_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scan_data = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="body_scans")
    recommendations = relationship("LifestyleRecommendation", back_populates="scan")

class LifestyleRecommendation(Base):
    """Model for storing lifestyle recommendations"""
    __tablename__ = "lifestyle_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("body_scans.id"))
    category = Column(String)
    priority = Column(Integer)
    description = Column(String)
    expected_impact = Column(Float)
    time_to_impact = Column(String)
    scientific_basis = Column(String)
    contraindications = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scan = relationship("BodyScan", back_populates="recommendations")