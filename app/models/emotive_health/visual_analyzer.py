from typing import Dict, List, Any, Optional
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import img_to_array
import cv2
import logging
from deepface import DeepFace
from app.core.config import settings

logger = logging.getLogger(__name__)

class VisualBiomarkerAnalyzer:
    """Advanced visual biomarker analysis for health assessment"""
    def __init__(self):
        # Load pre-trained models
        self.vgg_model = VGG16(weights='imagenet', include_top=False)
        self.emotion_model = tf.keras.models.load_model(
            settings.EMOTION_MODEL_PATH
        )
        
    async def analyze_visual_biomarkers(
        self,
        image_data: bytes
    ) -> Dict[str, Any]:
        """Analyze visual biomarkers for health assessment"""
        try:
            # Convert bytes to image
            image = self._bytes_to_image(image_data)
            
            # Detect face region
            face_data = self._detect_face(image)
            if not face_data:
                return {}
                
            # Extract comprehensive features
            features = self._extract_features(face_data)
            
            # Analyze emotional state
            emotional_state = self._analyze_emotional_state(face_data)
            
            # Analyze fatigue markers
            fatigue_markers = self._analyze_fatigue_markers(face_data)
            
            # Analyze skin health
            skin_health = self._analyze_skin_health(face_data)
            
            # Analyze symmetry
            symmetry = self._analyze_facial_symmetry(face_data)
            
            return {
                'emotional_state': emotional_state,
                'fatigue_markers': fatigue_markers,
                'skin_health': skin_health,
                'facial_symmetry': symmetry,
                'confidence': self._calculate_confidence(features)
            }
            
        except Exception as e:
            logger.error(f"Visual biomarker analysis error: {str(e)}")
            return {}

    def _bytes_to_image(
        self,
        image_data: bytes
    ) -> np.ndarray:
        """Convert bytes to OpenCV image"""
        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
            
        except Exception as e:
            logger.error(f"Image conversion error: {str(e)}")
            return None

    def _detect_face(
        self,
        image: np.ndarray
    ) -> Dict[str, Any]:
        """Detect and extract face region"""
        try:
            # Use DeepFace for face detection
            face_data = DeepFace.extract_faces(
                img_path=image,
                target_size=(224, 224),
                detector_backend='opencv'
            )[0]
            
            return face_data
            
        except Exception as e:
            logger.error(f"Face detection error: {str(e)}")
            return None

    def _extract_features(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Extract comprehensive visual features"""
        try:
            # Prepare image for VGG
            img = face_data['face']
            img = img_to_array(img)
            img = np.expand_dims(img, axis=0)
            
            # Extract VGG features
            vgg_features = self.vgg_model.predict(img)
            
            # Extract face landmarks
            landmarks = self._extract_landmarks(face_data)
            
            # Extract color features
            color_features = self._extract_color_features(face_data)
            
            return {
                'vgg_features': vgg_features,
                'landmarks': landmarks,
                'color_features': color_features
            }
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            return {}

    def _analyze_emotional_state(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze emotional state from facial expressions"""
        try:
            # Use DeepFace for emotion analysis
            emotion_analysis = DeepFace.analyze(
                img_path=face_data['face'],
                actions=['emotion'],
                detector_backend='opencv'
            )
            
            # Get dominant emotions
            emotions = emotion_analysis[0]['emotion']
            sorted_emotions = sorted(
                emotions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                'primary_emotion': {
                    'emotion': sorted_emotions[0][0],
                    'confidence': sorted_emotions[0][1]
                },
                'secondary_emotion': {
                    'emotion': sorted_emotions[1][0],
                    'confidence': sorted_emotions[1][1]
                },
                'emotional_stability': self._calculate_emotional_stability(
                    emotions
                )
            }
            
        except Exception as e:
            logger.error(f"Emotional state analysis error: {str(e)}")
            return {}

    def _analyze_fatigue_markers(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze facial markers of fatigue"""
        try:
            # Extract eye regions
            left_eye, right_eye = self._extract_eye_regions(face_data)
            
            # Calculate eye aspect ratio
            ear = self._calculate_eye_aspect_ratio(left_eye, right_eye)
            
            # Analyze dark circles
            dark_circles = self._analyze_dark_circles(face_data)
            
            # Analyze facial muscle tension
            muscle_tension = self._analyze_muscle_tension(face_data)
            
            return {
                'eye_fatigue': {
                    'eye_aspect_ratio': float(ear),
                    'dark_circles': dark_circles
                },
                'muscle_tension': muscle_tension,
                'overall_fatigue': self._calculate_fatigue_score([
                    ear,
                    dark_circles['severity'],
                    muscle_tension['tension_score']
                ])
            }
            
        except Exception as e:
            logger.error(f"Fatigue marker analysis error: {str(e)}")
            return {}

    def _analyze_skin_health(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze skin health markers"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(face_data['face'], cv2.COLOR_BGR2HSV)
            
            # Analyze skin tone
            skin_tone = self._analyze_skin_tone(hsv)
            
            # Analyze texture
            texture = self._analyze_skin_texture(face_data['face'])
            
            # Analyze color uniformity
            uniformity = self._analyze_color_uniformity(hsv)
            
            return {
                'skin_tone': skin_tone,
                'texture': texture,
                'uniformity': uniformity,
                'overall_health': self._calculate_skin_health_score([
                    skin_tone['evenness'],
                    texture['smoothness'],
                    uniformity['score']
                ])
            }
            
        except Exception as e:
            logger.error(f"Skin health analysis error: {str(e)}")
            return {}

    def _analyze_facial_symmetry(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze facial symmetry"""
        try:
            # Get face landmarks
            landmarks = face_data['landmarks']
            
            # Calculate landmark symmetry
            landmark_symmetry = self._calculate_landmark_symmetry(landmarks)
            
            # Calculate contour symmetry
            contour_symmetry = self._calculate_contour_symmetry(face_data['face'])
            
            # Calculate feature symmetry
            feature_symmetry = self._calculate_feature_symmetry(landmarks)
            
            return {
                'landmark_symmetry': landmark_symmetry,
                'contour_symmetry': contour_symmetry,
                'feature_symmetry': feature_symmetry,
                'overall_symmetry': np.mean([
                    landmark_symmetry['score'],
                    contour_symmetry['score'],
                    feature_symmetry['score']
                ])
            }
            
        except Exception as e:
            logger.error(f"Facial symmetry analysis error: {str(e)}")
            return {}

    def _extract_landmarks(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Extract facial landmarks"""
        try:
            return DeepFace.analyze(
                img_path=face_data['face'],
                actions=['landmarks'],
                detector_backend='opencv'
            )[0]['landmarks']
            
        except Exception as e:
            logger.error(f"Landmark extraction error: {str(e)}")
            return {}

    def _extract_color_features(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, np.ndarray]:
        """Extract color-based features"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(face_data['face'], cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(face_data['face'], cv2.COLOR_BGR2LAB)
            
            return {
                'hsv_hist': cv2.calcHist(
                    [hsv],
                    [0, 1],
                    None,
                    [180, 256],
                    [0, 180, 0, 256]
                ),
                'lab_hist': cv2.calcHist(
                    [lab],
                    [0],
                    None,
                    [256],
                    [0, 256]
                )
            }
            
        except Exception as e:
            logger.error(f"Color feature extraction error: {str(e)}")
            return {}

    def _extract_eye_regions(
        self,
        face_data: Dict[str, Any]
    ) -> tuple:
        """Extract left and right eye regions"""
        try:
            landmarks = face_data['landmarks']
            left_eye = landmarks['left_eye']
            right_eye = landmarks['right_eye']
            
            return left_eye, right_eye
            
        except Exception as e:
            logger.error(f"Eye region extraction error: {str(e)}")
            return None, None

    def _calculate_eye_aspect_ratio(
        self,
        left_eye: np.ndarray,
        right_eye: np.ndarray
    ) -> float:
        """Calculate eye aspect ratio for fatigue detection"""
        try:
            # Calculate the euclidean distances
            left_ear = self._eye_aspect_ratio(left_eye)
            right_ear = self._eye_aspect_ratio(right_eye)
            
            # Average the eye aspect ratios
            return (left_ear + right_ear) / 2.0
            
        except Exception as e:
            logger.error(f"Eye aspect ratio calculation error: {str(e)}")
            return 0.0

    def _eye_aspect_ratio(
        self,
        eye: np.ndarray
    ) -> float:
        """Helper function to calculate single eye aspect ratio"""
        try:
            # Calculate vertical distances
            A = np.linalg.norm(eye[1] - eye[5])
            B = np.linalg.norm(eye[2] - eye[4])
            
            # Calculate horizontal distance
            C = np.linalg.norm(eye[0] - eye[3])
            
            # Calculate eye aspect ratio
            ear = (A + B) / (2.0 * C)
            
            return float(ear)
            
        except Exception as e:
            logger.error(f"Single eye aspect ratio calculation error: {str(e)}")
            return 0.0

    def _analyze_dark_circles(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze dark circles under eyes"""
        try:
            # Extract under-eye regions
            left_eye, right_eye = self._extract_eye_regions(face_data)
            
            # Calculate darkness scores
            left_score = self._calculate_darkness_score(
                face_data['face'],
                left_eye
            )
            right_score = self._calculate_darkness_score(
                face_data['face'],
                right_eye
            )
            
            # Average the scores
            severity = (left_score + right_score) / 2.0
            
            return {
                'left_eye': float(left_score),
                'right_eye': float(right_score),
                'severity': float(severity)
            }
            
        except Exception as e:
            logger.error(f"Dark circles analysis error: {str(e)}")
            return {}

    def _calculate_darkness_score(
        self,
        image: np.ndarray,
        eye_region: np.ndarray
    ) -> float:
        """Calculate darkness score for under-eye region"""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Extract L channel
            l_channel = lab[:, :, 0]
            
            # Get under-eye region
            under_eye = l_channel[
                int(eye_region[4][1]):int(eye_region[4][1] + 20),
                int(eye_region[0][0]):int(eye_region[3][0])
            ]
            
            # Calculate darkness score
            darkness_score = 1 - (np.mean(under_eye) / 255.0)
            
            return float(darkness_score)
            
        except Exception as e:
            logger.error(f"Darkness score calculation error: {str(e)}")
            return 0.0

    def _analyze_muscle_tension(
        self,
        face_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze facial muscle tension"""
        try:
            landmarks = face_data['landmarks']
            
            # Calculate distances between key points
            jaw_tension = self._calculate_jaw_tension(landmarks)
            brow_tension = self._calculate_brow_tension(landmarks)
            mouth_tension = self._calculate_mouth_tension(landmarks)
            
            # Calculate overall tension score
            tension_score = np.mean([
                jaw_tension,
                brow_tension,
                mouth_tension
            ])
            
            return {
                'jaw_tension': float(jaw_tension),
                'brow_tension': float(brow_tension),
                'mouth_tension': float(mouth_tension),
                'tension_score': float(tension_score)
            }
            
        except Exception as e:
            logger.error(f"Muscle tension analysis error: {str(e)}")
            return {}

    def _calculate_jaw_tension(
        self,
        landmarks: Dict[str, np.ndarray]
    ) -> float:
        """Calculate jaw tension from landmarks"""
        try:
            jaw_points = landmarks['jaw']
            
            # Calculate angles between jaw points
            angles = []
            for i in range(1, len(jaw_points) - 1):
                angle = self._calculate_angle(
                    jaw_points[i-1],
                    jaw_points[i],
                    jaw_points[i+1]
                )
                angles.append(angle)
            
            # Calculate tension score
            tension = np.std(angles) / np.mean(angles)
            
            return float(tension)
            
        except Exception as e:
            logger.error(f"Jaw tension calculation error: {str(e)}")
            return 0.0

    def _calculate_brow_tension(
        self,
        landmarks: Dict[str, np.ndarray]
    ) -> float:
        """Calculate brow tension from landmarks"""
        try:
            left_brow = landmarks['left_eyebrow']
            right_brow = landmarks['right_eyebrow']
            
            # Calculate brow curvature
            left_curve = self._calculate_curvature(left_brow)
            right_curve = self._calculate_curvature(right_brow)
            
            # Calculate tension score
            tension = abs(left_curve - right_curve)
            
            return float(tension)
            
        except Exception as e:
            logger.error(f"Brow tension calculation error: {str(e)}")
            return 0.0

    def _calculate_mouth_tension(
        self,
        landmarks: Dict[str, np.ndarray]
    ) -> float:
        """Calculate mouth tension from landmarks"""
        try:
            mouth = landmarks['mouth']
            
            # Calculate mouth symmetry
            left_side = mouth[:len(mouth)//2]
            right_side = mouth[len(mouth)//2:]
            
            # Calculate tension score
            tension = np.mean([
                self._calculate_curvature(left_side),
                self._calculate_curvature(right_side)
            ])
            
            return float(tension)
            
        except Exception as e:
            logger.error(f"Mouth tension calculation error: {str(e)}")
            return 0.0

    def _calculate_angle(
        self,
        p1: np.ndarray,
        p2: np.ndarray,
        p3: np.ndarray
    ) -> float:
        """Calculate angle between three points"""
        try:
            v1 = p1 - p2
            v2 = p3 - p2
            
            cos_angle = np.dot(v1, v2) / (
                np.linalg.norm(v1) * np.linalg.norm(v2)
            )
            
            return np.arccos(cos_angle)
            
        except Exception as e:
            logger.error(f"Angle calculation error: {str(e)}")
            return 0.0

    def _calculate_curvature(
        self,
        points: np.ndarray
    ) -> float:
        """Calculate curvature of a set of points"""
        try:
            # Fit polynomial
            x = points[:, 0]
            y = points[:, 1]
            z = np.polyfit(x, y, 2)
            
            # Calculate curvature
            return abs(z[0])
            
        except Exception as e:
            logger.error(f"Curvature calculation error: {str(e)}")
            return 0.0

    def _analyze_skin_tone(
        self,
        hsv_image: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze skin tone characteristics"""
        try:
            # Extract Hue and Saturation channels
            h = hsv_image[:, :, 0]
            s = hsv_image[:, :, 1]
            
            # Calculate tone metrics
            tone_mean = np.mean(h)
            tone_std = np.std(h)
            saturation = np.mean(s)
            
            # Calculate evenness
            evenness = 1 - (tone_std / tone_mean)
            
            return {
                'tone_value': float(tone_mean),
                'saturation': float(saturation),
                'evenness': float(evenness)
            }
            
        except Exception as e:
            logger.error(f"Skin tone analysis error: {str(e)}")
            return {}

    def _analyze_skin_texture(
        self,
        image: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze skin texture characteristics"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture metrics
            smoothness = 1 - np.std(gray) / 255.0
            entropy_val = entropy(gray.ravel())
            
            return {
                'smoothness': float(smoothness),
                'entropy': float(entropy_val),
                'texture_score': float(
                    (smoothness + (1 - entropy_val/8)) / 2
                )
            }
            
        except Exception as e:
            logger.error(f"Skin texture analysis error: {str(e)}")
            return {}

    def _analyze_color_uniformity(
        self,
        hsv_image: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze color uniformity in skin regions"""
        try:
            # Calculate color statistics
            mean_color = np.mean(hsv_image, axis=(0,1))
            std_color = np.std(hsv_image, axis=(0,1))
            
            # Calculate uniformity score
            uniformity = 1 - np.mean(std_color/mean_color)
            
            return {
                'mean_color': mean_color.tolist(),
                'std_color': std_color.tolist(),
                'score': float(uniformity)
            }
            
        except Exception as e:
            logger.error(f"Color uniformity analysis error: {str(e)}")
            return {}

    def _calculate_landmark_symmetry(
        self,
        landmarks: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Calculate symmetry based on facial landmarks"""
        try:
            # Calculate midline
            nose_bridge = landmarks['nose_bridge']
            midline = np.mean(nose_bridge, axis=0)
            
            # Calculate symmetry scores for different features
            eye_sym = self._calculate_feature_symmetry_score(
                landmarks['left_eye'],
                landmarks['right_eye'],
                midline
            )
            brow_sym = self._calculate_feature_symmetry_score(
                landmarks['left_eyebrow'],
                landmarks['right_eyebrow'],
                midline
            )
            mouth_sym = self._calculate_feature_symmetry_score(
                landmarks['mouth'][:len(landmarks['mouth'])//2],
                landmarks['mouth'][len(landmarks['mouth'])//2:],
                midline
            )
            
            return {
                'eye_symmetry': float(eye_sym),
                'brow_symmetry': float(brow_sym),
                'mouth_symmetry': float(mouth_sym),
                'score': float(np.mean([eye_sym, brow_sym, mouth_sym]))
            }
            
        except Exception as e:
            logger.error(f"Landmark symmetry calculation error: {str(e)}")
            return {}

    def _calculate_feature_symmetry_score(
        self,
        left_points: np.ndarray,
        right_points: np.ndarray,
        midline: np.ndarray
    ) -> float:
        """Calculate symmetry score for a facial feature"""
        try:
            # Calculate distances from midline
            left_distances = np.linalg.norm(
                left_points - midline,
                axis=1
            )
            right_distances = np.linalg.norm(
                right_points - midline,
                axis=1
            )
            
            # Calculate symmetry score
            symmetry = 1 - (
                np.mean(np.abs(left_distances - right_distances)) /
                np.mean(left_distances)
            )
            
            return float(symmetry)
            
        except Exception as e:
            logger.error(f"Feature symmetry score calculation error: {str(e)}")
            return 0.0

    def _calculate_contour_symmetry(
        self,
        image: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate symmetry based on face contour"""
        try:
            # Get face contour
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Find face contour (largest contour)
            face_contour = max(contours, key=cv2.contourArea)
            
            # Calculate contour symmetry
            symmetry_score = self._calculate_contour_symmetry_score(face_contour)
            
            return {
                'score': float(symmetry_score),
                'contour_points': len(face_contour)
            }
            
        except Exception as e:
            logger.error(f"Contour symmetry calculation error: {str(e)}")
            return {}

    def _calculate_contour_symmetry_score(
        self,
        contour: np.ndarray
    ) -> float:
        """Calculate symmetry score for a contour"""
        try:
            # Get contour center
            M = cv2.moments(contour)
            cx = int(M['m10']/M['m00'])
            
            # Split contour into left and right
            left_points = []
            right_points = []
            for point in contour:
                if point[0][0] < cx:
                    left_points.append(point)
                else:
                    right_points.append(point)
            
            # Calculate symmetry score
            left_area = cv2.contourArea(np.array(left_points))
            right_area = cv2.contourArea(np.array(right_points))
            
            symmetry = 1 - abs(
                left_area - right_area
            ) / max(left_area, right_area)
            
            return float(symmetry)
            
        except Exception as e:
            logger.error(f"Contour symmetry score calculation error: {str(e)}")
            return 0.0

    def _calculate_feature_symmetry(
        self,
        landmarks: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Calculate symmetry based on facial features"""
        try:
            # Calculate feature centers
            left_eye_center = np.mean(landmarks['left_eye'], axis=0)
            right_eye_center = np.mean(landmarks['right_eye'], axis=0)
            nose_tip = landmarks['nose_bridge'][-1]
            mouth_center = np.mean(landmarks['mouth'], axis=0)
            
            # Calculate symmetry metrics
            horizontal_symmetry = self._calculate_horizontal_symmetry(
                left_eye_center,
                right_eye_center,
                nose_tip
            )
            vertical_symmetry = self._calculate_vertical_symmetry(
                nose_tip,
                mouth_center
            )
            
            return {
                'horizontal_symmetry': float(horizontal_symmetry),
                'vertical_symmetry': float(vertical_symmetry),
                'score': float((horizontal_symmetry + vertical_symmetry) / 2)
            }
            
        except Exception as e:
            logger.error(f"Feature symmetry calculation error: {str(e)}")
            return {}

    def _calculate_horizontal_symmetry(
        self,
        left_eye: np.ndarray,
        right_eye: np.ndarray,
        nose_tip: np.ndarray
    ) -> float:
        """Calculate horizontal symmetry score"""
        try:
            # Calculate distances
            left_dist = np.linalg.norm(left_eye - nose_tip)
            right_dist = np.linalg.norm(right_eye - nose_tip)
            
            # Calculate symmetry score
            symmetry = 1 - abs(
                left_dist - right_dist
            ) / max(left_dist, right_dist)
            
            return float(symmetry)
            
        except Exception as e:
            logger.error(f"Horizontal symmetry calculation error: {str(e)}")
            return 0.0

    def _calculate_vertical_symmetry(
        self,
        nose_tip: np.ndarray,
        mouth_center: np.ndarray
    ) -> float:
        """Calculate vertical symmetry score"""
        try:
            # Calculate vertical alignment
            horizontal_diff = abs(nose_tip[0] - mouth_center[0])
            vertical_dist = np.linalg.norm(nose_tip - mouth_center)
            
            # Calculate symmetry score
            symmetry = 1 - (horizontal_diff / vertical_dist)
            
            return float(symmetry)
            
        except Exception as e:
            logger.error(f"Vertical symmetry calculation error: {str(e)}")
            return 0.0

    def _calculate_emotional_stability(
        self,
        emotions: Dict[str, float]
    ) -> float:
        """Calculate emotional stability score"""
        try:
            # Sort emotions by intensity
            sorted_emotions = sorted(
                emotions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Calculate stability based on emotion distribution
            primary_intensity = sorted_emotions[0][1]
            secondary_intensity = sorted_emotions[1][1]
            
            stability = 1 - (
                abs(primary_intensity - secondary_intensity) /
                primary_intensity
            )
            
            return float(stability)
            
        except Exception as e:
            logger.error(f"Emotional stability calculation error: {str(e)}")
            return 0.0

    def _calculate_fatigue_score(
        self,
        markers: List[float]
    ) -> float:
        """Calculate overall fatigue score"""
        try:
            weights = [0.4, 0.3, 0.3]  # Weights for different markers
            return float(np.average(markers, weights=weights))
            
        except Exception as e:
            logger.error(f"Fatigue score calculation error: {str(e)}")
            return 0.0

    def _calculate_skin_health_score(
        self,
        markers: List[float]
    ) -> float:
        """Calculate overall skin health score"""
        try:
            weights = [0.4, 0.3, 0.3]  # Weights for different markers
            return float(np.average(markers, weights=weights))
            
        except Exception as e:
            logger.error(f"Skin health score calculation error: {str(e)}")
            return 0.0

    def _calculate_confidence(
        self,
        features: Dict[str, np.ndarray]
    ) -> float:
        """Calculate overall confidence score"""
        try:
            # Calculate feature quality scores
            vgg_confidence = np.mean(features['vgg_features']) > 0.5
            landmark_confidence = len(features['landmarks']) > 0
            color_confidence = np.mean(
                features['color_features']['hsv_hist']
            ) > 0
            
            return float(
                np.mean([
                    vgg_confidence,
                    landmark_confidence,
                    color_confidence
                ])
            )
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.0