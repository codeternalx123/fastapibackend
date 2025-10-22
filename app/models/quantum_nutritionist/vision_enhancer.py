from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from fastapi import HTTPException
import tensorflow as tf
from vertexai.vision import ImageAnalysisService
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import cv2
from scipy.spatial.distance import cdist
from app.core.config import settings

logger = logging.getLogger(__name__)

class ObjectDetectionEnhancer:
    """Enhanced object detection with spatial relationship mapping"""
    def __init__(self):
        self.vertex_ai = ImageAnalysisService()
        self.spatial_model = self._load_spatial_model()
        
    def _load_spatial_model(self) -> tf.keras.Model:
        """Load spatial relationship model"""
        return tf.keras.models.load_model(settings.SPATIAL_MODEL_PATH)

    async def enhance_detection(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance object detections with spatial relationships"""
        try:
            # Parallel enhancement pipeline
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._refine_boundaries,
                        image,
                        detections
                    ),
                    executor.submit(
                        self._analyze_spatial_relationships,
                        detections
                    ),
                    executor.submit(
                        self._detect_occlusions,
                        image,
                        detections
                    ),
                    executor.submit(
                        self._estimate_depths,
                        image,
                        detections
                    )
                ]
                
                results = await asyncio.gather(
                    *[asyncio.wrap_future(f) for f in futures]
                )
                
            # Combine enhancements
            enhanced_detections = self._combine_enhancements(
                detections,
                results
            )
            
            return enhanced_detections
            
        except Exception as e:
            logger.error(f"Detection enhancement error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Detection enhancement failed"
            )

    def _refine_boundaries(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Refine object boundaries using active contours"""
        refined = []
        for detection in detections:
            try:
                bbox = detection['bounding_box']
                roi = image[
                    bbox['y1']:bbox['y2'],
                    bbox['x1']:bbox['x2']
                ]
                
                # Convert to grayscale
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                
                # Apply active contour model
                contour = cv2.findContours(
                    gray,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_NONE
                )[0]
                
                # Refine boundary
                refined_contour = cv2.convexHull(contour[0])
                
                refined.append({
                    **detection,
                    'refined_contour': refined_contour
                })
                
            except Exception as e:
                logger.error(f"Boundary refinement error: {str(e)}")
                refined.append(detection)
                
        return refined

    def _analyze_spatial_relationships(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze spatial relationships between objects"""
        relationships = []
        for i, obj1 in enumerate(detections):
            obj_relationships = []
            for j, obj2 in enumerate(detections):
                if i != j:
                    relation = self._compute_spatial_relation(obj1, obj2)
                    if relation:
                        obj_relationships.append({
                            'object_id': j,
                            'relation': relation,
                            'confidence': self._compute_relation_confidence(
                                obj1,
                                obj2
                            )
                        })
            relationships.append(obj_relationships)
        return relationships

    def _detect_occlusions(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect and analyze occlusions between objects"""
        occlusions = []
        for i, obj1 in enumerate(detections):
            obj_occlusions = []
            for j, obj2 in enumerate(detections):
                if i != j:
                    occlusion = self._compute_occlusion(
                        image,
                        obj1,
                        obj2
                    )
                    if occlusion['overlap_ratio'] > 0:
                        obj_occlusions.append({
                            'object_id': j,
                            'occlusion': occlusion
                        })
            occlusions.append(obj_occlusions)
        return occlusions

    def _estimate_depths(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> List[float]:
        """Estimate relative depths of objects"""
        try:
            # Extract image features
            features = self._extract_depth_features(image)
            
            # Predict depths using spatial model
            depths = self.spatial_model.predict(features)
            
            return depths.tolist()
            
        except Exception as e:
            logger.error(f"Depth estimation error: {str(e)}")
            return [1.0] * len(detections)

    def _compute_spatial_relation(
        self,
        obj1: Dict[str, Any],
        obj2: Dict[str, Any]
    ) -> Optional[str]:
        """Compute spatial relationship between two objects"""
        # Get bounding boxes
        box1 = obj1['bounding_box']
        box2 = obj2['bounding_box']
        
        # Calculate centers
        center1 = (
            (box1['x1'] + box1['x2']) / 2,
            (box1['y1'] + box1['y2']) / 2
        )
        center2 = (
            (box2['x1'] + box2['x2']) / 2,
            (box2['y1'] + box2['y2']) / 2
        )
        
        # Calculate angle and distance
        angle = np.arctan2(
            center2[1] - center1[1],
            center2[0] - center1[0]
        )
        distance = np.sqrt(
            (center2[0] - center1[0])**2 +
            (center2[1] - center1[1])**2
        )
        
        # Determine relationship
        if distance < 50:  # Close proximity
            return 'adjacent'
        elif abs(angle) < np.pi/4:
            return 'right'
        elif abs(angle) > 3*np.pi/4:
            return 'left'
        elif angle > 0:
            return 'below'
        else:
            return 'above'

    def _compute_relation_confidence(
        self,
        obj1: Dict[str, Any],
        obj2: Dict[str, Any]
    ) -> float:
        """Compute confidence score for spatial relationship"""
        # Combine object detection confidences
        conf1 = obj1.get('confidence', 0.5)
        conf2 = obj2.get('confidence', 0.5)
        
        # Calculate distance-based confidence
        box1 = obj1['bounding_box']
        box2 = obj2['bounding_box']
        
        center1 = (
            (box1['x1'] + box1['x2']) / 2,
            (box1['y1'] + box1['y2']) / 2
        )
        center2 = (
            (box2['x1'] + box2['x2']) / 2,
            (box2['y1'] + box2['y2']) / 2
        )
        
        distance = np.sqrt(
            (center2[0] - center1[0])**2 +
            (center2[1] - center1[1])**2
        )
        
        # Distance confidence decreases with distance
        dist_conf = 1 / (1 + distance/100)
        
        # Combine confidences
        return conf1 * conf2 * dist_conf

    def _compute_occlusion(
        self,
        image: np.ndarray,
        obj1: Dict[str, Any],
        obj2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute occlusion between two objects"""
        box1 = obj1['bounding_box']
        box2 = obj2['bounding_box']
        
        # Calculate intersection
        x1 = max(box1['x1'], box2['x1'])
        y1 = max(box1['y1'], box2['y1'])
        x2 = min(box1['x2'], box2['x2'])
        y2 = min(box1['y2'], box2['y2'])
        
        if x1 < x2 and y1 < y2:
            intersection = (x2 - x1) * (y2 - y1)
            area1 = (
                (box1['x2'] - box1['x1']) *
                (box1['y2'] - box1['y1'])
            )
            area2 = (
                (box2['x2'] - box2['x1']) *
                (box2['y2'] - box2['y1'])
            )
            overlap_ratio = intersection / min(area1, area2)
            
            # Analyze occlusion edges
            edges = self._analyze_occlusion_edges(
                image,
                (x1, y1, x2, y2)
            )
            
            return {
                'overlap_ratio': overlap_ratio,
                'intersection_box': {
                    'x1': x1, 'y1': y1,
                    'x2': x2, 'y2': y2
                },
                'edge_analysis': edges
            }
        else:
            return {'overlap_ratio': 0.0}

    def _analyze_occlusion_edges(
        self,
        image: np.ndarray,
        intersection: Tuple[int, int, int, int]
    ) -> Dict[str, Any]:
        """Analyze edges in occlusion region"""
        x1, y1, x2, y2 = intersection
        roi = image[y1:y2, x1:x2]
        
        # Apply edge detection
        edges = cv2.Canny(roi, 100, 200)
        
        # Analyze edge directions
        directions = cv2.phase(
            cv2.Sobel(roi, cv2.CV_64F, 1, 0),
            cv2.Sobel(roi, cv2.CV_64F, 0, 1)
        )
        
        return {
            'edge_strength': float(np.mean(edges)),
            'edge_directions': directions.tolist()
        }

    def _extract_depth_features(
        self,
        image: np.ndarray
    ) -> np.ndarray:
        """Extract features for depth estimation"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract gradient features
        gradient_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
        gradient_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
        
        # Calculate gradient magnitude and direction
        magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        direction = np.arctan2(gradient_y, gradient_x)
        
        # Create feature vector
        features = np.concatenate([
            magnitude.flatten(),
            direction.flatten()
        ])
        
        return features

    def _combine_enhancements(
        self,
        detections: List[Dict[str, Any]],
        enhancements: List[Any]
    ) -> List[Dict[str, Any]]:
        """Combine all enhancements into final detections"""
        refined_boundaries, spatial_relations, occlusions, depths = enhancements
        
        enhanced = []
        for i, detection in enumerate(detections):
            enhanced.append({
                **detection,
                'refined_boundary': refined_boundaries[i],
                'spatial_relations': spatial_relations[i],
                'occlusions': occlusions[i],
                'relative_depth': depths[i]
            })
            
        return enhanced