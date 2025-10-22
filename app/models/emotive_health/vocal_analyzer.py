from typing import Dict, List, Any, Optional
import numpy as np
from scipy import signal
from scipy.stats import entropy
import librosa
import librosa.feature
import logging
import tensorflow as tf
from app.core.config import settings

logger = logging.getLogger(__name__)

class VocalBiomarkerAnalyzer:
    """Advanced vocal biomarker analysis"""
    def __init__(self):
        self.model = tf.keras.models.load_model(settings.VOCAL_MODEL_PATH)
        
    async def analyze_vocal_biomarkers(
        self,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Analyze vocal biomarkers for emotion and stress"""
        try:
            # Load audio
            y, sr = librosa.load(audio_data)
            
            # Extract comprehensive features
            features = self._extract_features(y, sr)
            
            # Analyze stress markers
            stress_markers = self._analyze_stress_markers(features)
            
            # Analyze emotional content
            emotional_content = self._analyze_emotional_content(features)
            
            # Analyze voice quality
            voice_quality = self._analyze_voice_quality(y, sr)
            
            return {
                'stress_markers': stress_markers,
                'emotional_content': emotional_content,
                'voice_quality': voice_quality,
                'confidence': self._calculate_confidence(features)
            }
            
        except Exception as e:
            logger.error(f"Vocal biomarker analysis error: {str(e)}")
            return {}

    def _extract_features(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, np.ndarray]:
        """Extract comprehensive vocal features"""
        features = {}
        
        # Spectral features
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            y=y,
            sr=sr
        )
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
            y=y,
            sr=sr
        )
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            y=y,
            sr=sr
        )
        
        # Rhythm features
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = tempo
        features['beats'] = beats
        
        # MFCCs
        features['mfccs'] = librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=13
        )
        
        # Chromagram
        features['chroma'] = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Zero crossing rate
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(y)
        
        # Root Mean Square Energy
        features['rmse'] = librosa.feature.rms(y=y)
        
        # Onset strength
        features['onset_env'] = librosa.onset.onset_strength(y=y, sr=sr)
        
        return features

    def _analyze_stress_markers(
        self,
        features: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Analyze stress markers in voice"""
        try:
            # Calculate jitter
            jitter = self._calculate_jitter(features['zero_crossing_rate'])
            
            # Calculate shimmer
            shimmer = self._calculate_shimmer(features['rmse'])
            
            # Analyze voice breaks
            voice_breaks = self._analyze_voice_breaks(
                features['zero_crossing_rate']
            )
            
            # Calculate HNR (Harmonics-to-Noise Ratio)
            hnr = self._calculate_hnr(features)
            
            return {
                'jitter': jitter,
                'shimmer': shimmer,
                'voice_breaks': voice_breaks,
                'hnr': hnr,
                'stress_level': self._calculate_stress_level([
                    jitter,
                    shimmer,
                    voice_breaks,
                    hnr
                ])
            }
            
        except Exception as e:
            logger.error(f"Stress marker analysis error: {str(e)}")
            return {}

    def _analyze_emotional_content(
        self,
        features: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Analyze emotional content in voice"""
        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)
            
            # Get model predictions
            predictions = self.model.predict(feature_vector)
            
            # Process predictions
            emotions = self._process_emotion_predictions(predictions)
            
            # Calculate emotional stability
            stability = self._calculate_emotional_stability(emotions)
            
            return {
                'primary_emotion': emotions['primary'],
                'secondary_emotion': emotions['secondary'],
                'emotional_stability': stability,
                'confidence': emotions['confidence']
            }
            
        except Exception as e:
            logger.error(f"Emotional content analysis error: {str(e)}")
            return {}

    def _analyze_voice_quality(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """Analyze voice quality metrics"""
        try:
            # Calculate pitch
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7')
            )
            
            # Calculate formants
            formants = self._calculate_formants(y, sr)
            
            # Analyze voice clarity
            clarity = self._analyze_voice_clarity(y, sr)
            
            return {
                'pitch_statistics': {
                    'mean': np.mean(f0[voiced_flag]),
                    'std': np.std(f0[voiced_flag]),
                    'range': np.ptp(f0[voiced_flag])
                },
                'formants': formants,
                'clarity': clarity,
                'voicing_ratio': np.mean(voiced_flag)
            }
            
        except Exception as e:
            logger.error(f"Voice quality analysis error: {str(e)}")
            return {}

    def _calculate_jitter(
        self,
        zero_crossings: np.ndarray
    ) -> float:
        """Calculate jitter (pitch perturbation)"""
        try:
            # Calculate period lengths
            periods = np.diff(
                np.where(zero_crossings > zero_crossings.mean())[0]
            )
            
            # Calculate jitter
            jitter = np.mean(np.abs(np.diff(periods))) / np.mean(periods)
            
            return float(jitter)
            
        except Exception as e:
            logger.error(f"Jitter calculation error: {str(e)}")
            return 0.0

    def _calculate_shimmer(
        self,
        rmse: np.ndarray
    ) -> float:
        """Calculate shimmer (amplitude perturbation)"""
        try:
            # Calculate amplitude differences
            amp_diff = np.abs(np.diff(rmse))
            
            # Calculate shimmer
            shimmer = np.mean(amp_diff) / np.mean(rmse)
            
            return float(shimmer)
            
        except Exception as e:
            logger.error(f"Shimmer calculation error: {str(e)}")
            return 0.0

    def _analyze_voice_breaks(
        self,
        zero_crossings: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze voice breaks"""
        try:
            # Find potential breaks
            potential_breaks = np.where(
                zero_crossings < 0.1 * zero_crossings.mean()
            )[0]
            
            # Analyze break patterns
            break_patterns = np.diff(potential_breaks)
            
            return {
                'count': len(potential_breaks),
                'mean_duration': float(np.mean(break_patterns)),
                'std_duration': float(np.std(break_patterns))
            }
            
        except Exception as e:
            logger.error(f"Voice break analysis error: {str(e)}")
            return {}

    def _calculate_hnr(
        self,
        features: Dict[str, np.ndarray]
    ) -> float:
        """Calculate Harmonics-to-Noise Ratio"""
        try:
            # Extract harmonics
            harmonics = np.sum(features['chroma'], axis=0)
            
            # Calculate noise
            noise = features['spectral_bandwidth'].flatten()
            
            # Calculate HNR
            hnr = 20 * np.log10(np.mean(harmonics) / np.mean(noise))
            
            return float(hnr)
            
        except Exception as e:
            logger.error(f"HNR calculation error: {str(e)}")
            return 0.0

    def _calculate_formants(
        self,
        y: np.ndarray,
        sr: int
    ) -> List[float]:
        """Calculate formant frequencies"""
        try:
            # Get spectrogram
            D = librosa.stft(y)
            
            # Get magnitude
            S = np.abs(D)
            
            # Find peaks in frequency domain
            freqs = librosa.fft_frequencies(sr=sr)
            peaks = signal.find_peaks(np.mean(S, axis=1))[0]
            
            # Get formant frequencies
            formants = freqs[peaks][:4]  # First 4 formants
            
            return formants.tolist()
            
        except Exception as e:
            logger.error(f"Formant calculation error: {str(e)}")
            return []

    def _analyze_voice_clarity(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, float]:
        """Analyze voice clarity metrics"""
        try:
            # Calculate spectral flatness
            flatness = np.mean(
                librosa.feature.spectral_flatness(y=y)
            )
            
            # Calculate spectral contrast
            contrast = np.mean(
                librosa.feature.spectral_contrast(y=y, sr=sr)
            )
            
            return {
                'flatness': float(flatness),
                'contrast': float(contrast),
                'clarity_score': float(contrast / (1 + flatness))
            }
            
        except Exception as e:
            logger.error(f"Voice clarity analysis error: {str(e)}")
            return {}

    def _prepare_feature_vector(
        self,
        features: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """Prepare feature vector for emotion prediction"""
        try:
            # Combine features
            feature_vector = np.concatenate([
                np.mean(features['mfccs'], axis=1),
                np.mean(features['chroma'], axis=1),
                [np.mean(features['spectral_centroid'])],
                [np.mean(features['spectral_bandwidth'])],
                [np.mean(features['spectral_rolloff'])],
                [np.mean(features['zero_crossing_rate'])],
                [np.mean(features['rmse'])]
            ])
            
            return feature_vector.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Feature vector preparation error: {str(e)}")
            return np.array([])

    def _process_emotion_predictions(
        self,
        predictions: np.ndarray
    ) -> Dict[str, Any]:
        """Process emotion predictions"""
        try:
            # Get emotion labels
            emotions = [
                'neutral',
                'happy',
                'sad',
                'angry',
                'fearful',
                'disgust',
                'surprised'
            ]
            
            # Get top emotions
            top_indices = np.argsort(predictions[0])[-2:]
            
            return {
                'primary': {
                    'emotion': emotions[top_indices[-1]],
                    'score': float(predictions[0][top_indices[-1]])
                },
                'secondary': {
                    'emotion': emotions[top_indices[-2]],
                    'score': float(predictions[0][top_indices[-2]])
                },
                'confidence': float(
                    predictions[0][top_indices[-1]] -
                    predictions[0][top_indices[-2]]
                )
            }
            
        except Exception as e:
            logger.error(f"Emotion prediction processing error: {str(e)}")
            return {}

    def _calculate_emotional_stability(
        self,
        emotions: Dict[str, Any]
    ) -> float:
        """Calculate emotional stability score"""
        try:
            # Get emotion intensities
            primary_intensity = emotions['primary']['score']
            secondary_intensity = emotions['secondary']['score']
            
            # Calculate stability based on emotion distribution
            stability = 1 - (
                abs(primary_intensity - secondary_intensity) /
                primary_intensity
            )
            
            return float(stability)
            
        except Exception as e:
            logger.error(f"Emotional stability calculation error: {str(e)}")
            return 0.0

    def _calculate_confidence(
        self,
        features: Dict[str, np.ndarray]
    ) -> float:
        """Calculate overall confidence score"""
        try:
            # Calculate feature quality scores
            quality_scores = [
                np.mean(features['zero_crossing_rate']) > 0.01,
                np.mean(features['rmse']) > 0.1,
                np.std(features['mfccs']) > 0.1,
                np.mean(features['spectral_centroid']) > 0
            ]
            
            return float(np.mean(quality_scores))
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.0