from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.deps import get_current_user, get_db
from app.models.database import User
from app.models.advanced_scanner import ContinuousLearningManager, CompoundDatabase
from app.models.tumor_analyzer import TumorAnalyzer
from app.models.body_scanner import BodyScanner, LifestyleOptimizer
from app.models.schemas.advanced import (
    TumorAnalysisRequest,
    TumorAnalysisResponse,
    BodyScanResponse,
    LifestyleRecommendations,
    CancerProgressionScore
)
import io
import logging

logger = logging.getLogger('app')
router = APIRouter()

# Initialize components
scanner_manager = ContinuousLearningManager()
compound_db = CompoundDatabase()
tumor_analyzer = TumorAnalyzer()
body_scanner = BodyScanner()
lifestyle_optimizer = LifestyleOptimizer()

@router.post("/analyze/food", response_model=Dict[str, Any])
async def analyze_food_advanced(
    image: UploadFile = File(...),
    spectral_data: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced food analysis using quantum-enhanced ML model
    """
    try:
        # Read image and spectral data
        image_data = await image.read()
        spectral_data = await spectral_data.read() if spectral_data else None
        
        # Process with advanced scanner
        scan_results = await scanner_manager.process_scan(
            image_data,
            spectral_data,
            user_id=current_user.id
        )
        
        # Update model with new data
        accuracy = await scanner_manager.update_model({
            'image': scan_results['image_features'],
            'spectral': scan_results['spectral_features'],
            'compounds': scan_results['detected_compounds'],
            'interactions': scan_results['compound_interactions']
        })
        
        logger.info(f"Model accuracy after update: {accuracy}%")
        
        return {
            'scan_results': scan_results,
            'model_accuracy': accuracy,
            'database_updates': compound_db.get_recent_updates()
        }
    except Exception as e:
        logger.error(f"Error in advanced food analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/tumor", response_model=TumorAnalysisResponse)
async def analyze_tumor(
    request: TumorAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze tumor profile using quantum computing
    """
    try:
        analysis = await tumor_analyzer.analyze_tumor_profile(
            genomic_data=request.genomic_data,
            biopsy_results=request.biopsy_results,
            blood_panel=request.blood_panel
        )
        
        return {
            'analysis_id': analysis['analysis_id'],
            'tumor_profile': analysis['tumor_profile'],
            'vulnerabilities': analysis['vulnerabilities'],
            'recommended_interventions': analysis['recommended_targets'],
            'confidence_score': analysis['confidence_score']
        }
    except Exception as e:
        logger.error(f"Error in tumor analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan/body", response_model=BodyScanResponse)
async def perform_body_scan(
    scan_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process body scan data and generate insights
    """
    try:
        # Get user profile
        profile = current_user.health_profiles[-1]
        
        # Process body scan
        metrics = await body_scanner.process_scan(
            scan_data=scan_data,
            user_profile={
                'cancer_type': profile.conditions.get('cancer_type'),
                'treatment_stage': profile.conditions.get('treatment_stage'),
                'age': profile.age,
                'weight': profile.weight
            }
        )
        
        return {
            'scan_id': metrics.scan_id,
            'metrics': {
                'inflammation': metrics.inflammation_level,
                'stress': metrics.stress_level,
                'sleep': metrics.sleep_quality,
                'tumor': metrics.tumor_metrics,
                'immune': metrics.immune_markers,
                'metabolic': metrics.metabolic_markers
            },
            'timestamp': metrics.timestamp
        }
    except Exception as e:
        logger.error(f"Error in body scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/lifestyle", response_model=LifestyleRecommendations)
async def optimize_lifestyle(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate holistic lifestyle recommendations
    """
    try:
        # Get latest metrics
        metrics = body_scanner.get_metrics(scan_id)
        if not metrics:
            raise HTTPException(status_code=404, detail="Scan not found")
            
        # Get current plan
        current_plan = db.query(TreatmentPlan).filter(
            TreatmentPlan.user_id == current_user.id,
            TreatmentPlan.status == "active"
        ).first()
        
        # Generate recommendations
        recommendations = await lifestyle_optimizer.generate_recommendations(
            body_metrics=metrics,
            user_profile=current_user.health_profiles[-1],
            current_plan=current_plan.dict() if current_plan else None
        )
        
        return recommendations
    except Exception as e:
        logger.error(f"Error in lifestyle optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/cpps", response_model=CancerProgressionScore)
async def get_cancer_progression_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current Cancer Progression Potential Score (CPPS)
    """
    try:
        # Get latest metrics
        latest_scan = body_scanner.get_latest_scan(current_user.id)
        if not latest_scan:
            raise HTTPException(status_code=404, detail="No recent scan data found")
            
        # Calculate CPPS
        cpps = lifestyle_optimizer._calculate_cpps(
            metrics=latest_scan,
            user_profile=current_user.health_profiles[-1]
        )
        
        return {
            'cpps': cpps,
            'interpretation': _interpret_cpps(cpps),
            'recommendations': lifestyle_optimizer._calculate_expected_impact(cpps),
            'timestamp': latest_scan.timestamp
        }
    except Exception as e:
        logger.error(f"Error calculating CPPS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _interpret_cpps(cpps: float) -> str:
    """Interpret CPPS score"""
    if cpps < 30:
        return "Excellent - Cancer progression potential is low"
    elif cpps < 50:
        return "Good - Moderate cancer progression potential"
    elif cpps < 70:
        return "Concerning - Elevated cancer progression potential"
    else:
        return "Critical - High cancer progression potential"