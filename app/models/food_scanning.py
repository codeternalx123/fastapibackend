from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class FoodScan(Base):
    __tablename__ = "food_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    scan_type = Column(String)  # 'camera' or 'hyperspectral'
    timestamp = Column(DateTime, default=datetime.utcnow)
    synergy_score = Column(Float)
    molecular_compounds = Column(JSON)  # Detected compounds and their concentrations
    nutritional_data = Column(JSON)
    cancer_markers = Column(JSON)  # Cancer-related compounds detected
    warning_flags = Column(ARRAY(String))
    analysis_metadata = Column(JSON)  # Processing metadata and confidence scores
    
    user = relationship("User", back_populates="food_scans")
    recommendations = relationship("FoodRecommendation", back_populates="scan")

class FoodRecommendation(Base):
    __tablename__ = "food_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("food_scans.id"))
    compound_name = Column(String)
    recommendation_type = Column(String)  # 'avoid', 'increase', 'moderate'
    reason = Column(String)
    impact_score = Column(Float)
    alternative_foods = Column(JSON)
    medical_references = Column(JSON)
    
    scan = relationship("FoodScan", back_populates="recommendations")

class MolecularCompound(Base):
    __tablename__ = "molecular_compounds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    chemical_formula = Column(String)
    molecular_weight = Column(Float)
    cancer_relation = Column(JSON)  # How this compound relates to different cancer types
    treatment_interactions = Column(JSON)  # Interactions with different treatments
    spectral_signature = Column(JSON)  # Spectral data for identification
    safety_data = Column(JSON)
    research_references = Column(JSON)

class SpectralSignature(Base):
    __tablename__ = "spectral_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    compound_id = Column(Integer, ForeignKey("molecular_compounds.id"))
    wavelength_range = Column(String)
    absorption_peaks = Column(JSON)
    reference_spectrum = Column(JSON)
    calibration_data = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)