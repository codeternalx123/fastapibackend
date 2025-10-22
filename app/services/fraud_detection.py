"""
Quantum-resistant fraud detection system
Using quantum-inspired algorithms for pattern recognition
"""

import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class QuantumFraudDetection:
    """
    Implements quantum-inspired anomaly detection for payment fraud
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.detector = IsolationForest(
            n_estimators=200,
            max_samples='auto',
            contamination=0.01,
            random_state=42
        )
        self.historical_data = []
        self.feature_names = [
            'amount',
            'frequency',
            'time_pattern',
            'location_pattern',
            'device_pattern'
        ]

    def extract_features(self, transaction: Dict[str, Any]) -> List[float]:
        """
        Extract relevant features for fraud detection
        """
        # Amount normalization
        amount = float(transaction['amount'])
        
        # Transaction frequency in last hour
        recent_transactions = [
            t for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and (datetime.now() - t['timestamp']) < timedelta(hours=1)
        ]
        frequency = len(recent_transactions)
        
        # Time pattern analysis
        hour = transaction['timestamp'].hour
        time_pattern = np.sin(2 * np.pi * hour / 24)  # Circular feature
        
        # Location pattern
        location_pattern = self._calculate_location_risk(
            transaction.get('location', {}),
            transaction['user_id']
        )
        
        # Device pattern
        device_pattern = self._calculate_device_risk(
            transaction.get('device_info', {}),
            transaction['user_id']
        )
        
        return [
            amount,
            frequency,
            time_pattern,
            location_pattern,
            device_pattern
        ]

    def _calculate_location_risk(
        self,
        location: Dict[str, Any],
        user_id: str
    ) -> float:
        """
        Calculate location-based risk score
        """
        if not location:
            return 1.0  # High risk for missing location
            
        # Get user's common locations
        user_locations = [
            t['location'] for t in self.historical_data
            if t['user_id'] == user_id
            and 'location' in t
        ]
        
        if not user_locations:
            return 0.5  # Moderate risk for new users
            
        # Calculate distance from common locations
        distances = []
        for loc in user_locations:
            if loc:
                distance = np.sqrt(
                    (loc.get('latitude', 0) - location.get('latitude', 0)) ** 2 +
                    (loc.get('longitude', 0) - location.get('longitude', 0)) ** 2
                )
                distances.append(distance)
        
        if distances:
            return min(distances) / max(1, max(distances))
        return 0.5

    def _calculate_device_risk(
        self,
        device_info: Dict[str, Any],
        user_id: str
    ) -> float:
        """
        Calculate device-based risk score
        """
        if not device_info:
            return 1.0  # High risk for missing device info
            
        # Get user's known devices
        user_devices = [
            t['device_info'] for t in self.historical_data
            if t['user_id'] == user_id
            and 'device_info' in t
        ]
        
        if not user_devices:
            return 0.5  # Moderate risk for new users
            
        # Check if device is known
        device_fingerprint = self._create_device_fingerprint(device_info)
        known_fingerprints = [
            self._create_device_fingerprint(d)
            for d in user_devices
            if d
        ]
        
        if device_fingerprint in known_fingerprints:
            return 0.0  # Low risk for known device
        return 0.8  # High risk for unknown device

    def _create_device_fingerprint(self, device_info: Dict[str, Any]) -> str:
        """
        Create a unique device fingerprint
        """
        relevant_fields = [
            'user_agent',
            'os',
            'browser',
            'screen_resolution',
            'timezone'
        ]
        
        fingerprint_parts = []
        for field in relevant_fields:
            value = device_info.get(field, '')
            if value:
                fingerprint_parts.append(f"{field}:{value}")
        
        return '|'.join(fingerprint_parts)

    def train(self, historical_transactions: List[Dict[str, Any]]):
        """
        Train the fraud detection model on historical data
        """
        self.historical_data = historical_transactions
        
        if not historical_transactions:
            return
            
        # Extract features from historical data
        X = np.array([
            self.extract_features(t)
            for t in historical_transactions
        ])
        
        # Fit scaler and detector
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.detector.fit(X_scaled)
        
        # Save the model
        joblib.dump(self.detector, 'fraud_detector.joblib')

    def detect_fraud(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential fraud in a transaction
        """
        # Extract and scale features
        features = self.extract_features(transaction)
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        
        # Get anomaly score (-1 for fraudulent, 1 for normal)
        score = self.detector.score_samples(X_scaled)[0]
        
        # Calculate fraud probability
        fraud_probability = 1 - (score + 1) / 2
        
        # Define risk levels
        risk_level = 'high' if fraud_probability > 0.8 else \
                    'medium' if fraud_probability > 0.5 else 'low'
        
        # Generate feature importance
        feature_importance = dict(zip(
            self.feature_names,
            np.abs(features / np.sum(np.abs(features)))
        ))
        
        return {
            'is_fraudulent': fraud_probability > 0.8,
            'fraud_probability': fraud_probability,
            'risk_level': risk_level,
            'feature_importance': feature_importance,
            'anomaly_score': score,
            'timestamp': datetime.now()
        }

    def update_model(self, transaction: Dict[str, Any], is_fraud: bool):
        """
        Update the model with new transaction data
        """
        transaction['timestamp'] = datetime.now()
        self.historical_data.append(transaction)
        
        # Retrain model periodically
        if len(self.historical_data) % 1000 == 0:
            self.train(self.historical_data)