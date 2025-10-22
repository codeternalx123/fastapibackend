from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.deps import get_current_user, get_db
from app.models.database import User
from app.models.food_scanning import FoodScan, FoodRecommendation
from app.services.food_scanner import FoodScanner, QuantumFoodAnalyzer
from app.models.schemas import (
    FoodScanRequest,
    FoodScanResponse,
    FoodRecommendationResponse,
    CompoundAnalysisResponse
)
import io
import logging

logger = logging.getLogger('app')
router = APIRouter()

# Initialize scanners
food_scanner = FoodScanner()
quantum_analyzer = QuantumFoodAnalyzer()

@router.post("/scan", response_model=FoodScanResponse)
async def scan_food(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan food using device camera and analyze its molecular composition
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Process image and detect compounds
        scan_results = await food_scanner.process_image(image_data)
        
        # Get user's current health state
        current_state = {
            "stress_level": current_user.health_profiles[-1].stress_score,
            "inflammation_markers": current_user.health_profiles[-1].conditions.get("inflammation", 0),
            "fasting_state": _check_fasting_state(current_user)
        }
        
        # Perform quantum analysis
        analysis_results = await quantum_analyzer.analyze_food_synergy(
            compounds=scan_results['compounds'],
            user_profile={
                "cancer_subtype": current_user.health_profiles[-1].conditions.get("cancer_type"),
                "treatment_stage": current_user.health_profiles[-1].conditions.get("treatment_stage"),
                "current_treatment": current_user.health_profiles[-1].medications
            },
            current_state=current_state
        )
        
        # Save scan results
        db_scan = FoodScan(
            user_id=current_user.id,
            scan_type="camera",
            synergy_score=analysis_results['synergy_score'],
            molecular_compounds=scan_results['compounds'],
            cancer_markers=_extract_cancer_markers(scan_results['compounds']),
            warning_flags=[w['message'] for w in analysis_results['warnings']],
            analysis_metadata={
                'confidence_scores': scan_results['confidence_scores'],
                'timestamp': scan_results['timestamp']
            }
        )
        db.add(db_scan)
        
        # Save recommendations
        for rec in analysis_results['recommendations']:
            db_rec = FoodRecommendation(
                scan_id=db_scan.id,
                recommendation_type=rec['type'],
                reason=rec['message'],
                alternative_foods=rec.get('items', [])
            )
            db.add(db_rec)
        
        db.commit()
        db.refresh(db_scan)
        
        return {
            'scan_id': db_scan.id,
            'synergy_score': analysis_results['synergy_score'],
            'warnings': analysis_results['warnings'],
            'recommendations': analysis_results['recommendations'],
            'detected_compounds': scan_results['compounds'],
            'confidence_scores': scan_results['confidence_scores']
        }
        
    except Exception as e:
        logger.error(f"Error during food scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan/{scan_id}/compounds", response_model=CompoundAnalysisResponse)
async def get_compound_analysis(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis of compounds from a previous scan
    """
    scan = db.query(FoodScan).filter(
        FoodScan.id == scan_id,
        FoodScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        'compounds': scan.molecular_compounds,
        'cancer_markers': scan.cancer_markers,
        'analysis_metadata': scan.analysis_metadata,
        'warning_flags': scan.warning_flags
    }

@router.get("/scan/{scan_id}/recommendations", response_model=FoodRecommendationResponse)
async def get_scan_recommendations(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed recommendations for a previous scan
    """
    recommendations = db.query(FoodRecommendation).filter(
        FoodRecommendation.scan_id == scan_id
    ).all()
    
    if not recommendations:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    
    return {
        'recommendations': [
            {
                'type': rec.recommendation_type,
                'reason': rec.reason,
                'alternatives': rec.alternative_foods
            }
            for rec in recommendations
        ]
    }

def _check_fasting_state(user: User) -> bool:
    """Check if user is currently in a fasting state"""
    # Implementation would depend on your fasting tracking system
    return False

def _extract_cancer_markers(compounds: List[dict]) -> dict:
    """Extract cancer-relevant markers from compounds"""
    markers = {}
    for compound in compounds:
        if compound.get('cancer_relation'):
            markers[compound['name']] = compound['cancer_relation']
    return markers