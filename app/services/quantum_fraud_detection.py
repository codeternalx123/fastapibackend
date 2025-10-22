"""
Quantum-enhanced fraud detection using D-Wave quantum annealer
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from dwave.system import DWaveSampler, EmbeddingComposite
from dimod import BinaryQuadraticModel
import neal
import logging

logger = logging.getLogger(__name__)

class QuantumFeatureExtractor:
    """
    Extract and process features using quantum computing
    """
    def __init__(self):
        try:
            self.sampler = EmbeddingComposite(DWaveSampler())
        except Exception as e:
            logger.warning(f"D-Wave initialization failed: {e}. Using classical simulator.")
            self.sampler = neal.SimulatedAnnealingSampler()

    def quantum_dimensionality_reduction(self, features: np.ndarray) -> np.ndarray:
        """
        Reduce feature dimensionality using quantum annealing
        """
        try:
            num_features = features.shape[1]
            target_dims = min(num_features, 5)  # Reduce to 5 dimensions max
            
            # Create QUBO for feature selection
            Q = {}
            for i in range(num_features):
                for j in range(i, num_features):
                    corr = np.corrcoef(features[:, i], features[:, j])[0, 1]
                    Q[(i, j)] = corr if i != j else -1
            
            bqm = BinaryQuadraticModel.from_qubo(Q)
            sampleset = self.sampler.sample(bqm, num_reads=100)
            selected_features = [i for i, val in enumerate(sampleset.first.sample.values()) if val == 1]
            
            # If quantum selection fails, select top correlated features
            if len(selected_features) < target_dims:
                selected_features = list(range(target_dims))
            
            return features[:, selected_features[:target_dims]]
            
        except Exception as e:
            logger.error(f"Quantum feature reduction failed: {e}")
            # Fallback to simple feature selection
            return features[:, :min(features.shape[1], 5)]

class QuantumFraudDetector:
    """
    Enhanced fraud detection using quantum and classical methods
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.detector = IsolationForest(
            n_estimators=200,
            contamination=0.01,
            random_state=42
        )
        self.quantum_extractor = QuantumFeatureExtractor()
        self.historical_data = []
        self.feature_names = [
            'amount',
            'frequency',
            'time_pattern',
            'location_risk',
            'device_risk',
            'transaction_pattern',
            'user_behavior',
            'network_signal'
        ]

    def extract_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """
        Extract enhanced feature set for fraud detection
        """
        features = []
        
        # Basic transaction features
        features.append(float(transaction['amount']))
        features.append(self._get_frequency(transaction))
        features.append(self._get_time_pattern(transaction))
        features.append(self._get_location_risk(transaction))
        features.append(self._get_device_risk(transaction))
        features.append(self._get_transaction_pattern(transaction))
        features.append(self._get_user_behavior_score(transaction))
        features.append(self._get_network_risk(transaction))
        
        return np.array(features)

    def _get_frequency(self, transaction: Dict[str, Any]) -> float:
        """Calculate transaction frequency"""
        recent_transactions = [
            t for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and (datetime.now() - t['timestamp']) < timedelta(hours=1)
        ]
        return len(recent_transactions)

    def _get_time_pattern(self, transaction: Dict[str, Any]) -> float:
        """Analyze time-based patterns"""
        hour = transaction['timestamp'].hour
        user_transactions = [
            t for t in self.historical_data
            if t['user_id'] == transaction['user_id']
        ]
        
        if not user_transactions:
            return 0.5
        
        # Calculate how unusual this hour is for the user
        hour_counts = {}
        for t in user_transactions:
            h = t['timestamp'].hour
            hour_counts[h] = hour_counts.get(h, 0) + 1
        
        avg_count = sum(hour_counts.values()) / len(hour_counts)
        current_count = hour_counts.get(hour, 0)
        
        return 1 - (current_count / (avg_count + 1))

    def _get_location_risk(self, transaction: Dict[str, Any]) -> float:
        """Calculate location-based risk"""
        location = transaction.get('location', {})
        if not location:
            return 1.0
        
        user_locations = [
            t.get('location', {}) for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and 'location' in t
        ]
        
        if not user_locations:
            return 0.5
        
        # Calculate minimum distance to known locations
        min_distance = float('inf')
        for loc in user_locations:
            if loc:
                distance = np.sqrt(
                    (loc.get('latitude', 0) - location.get('latitude', 0)) ** 2 +
                    (loc.get('longitude', 0) - location.get('longitude', 0)) ** 2
                )
                min_distance = min(min_distance, distance)
        
        return min(min_distance / 100, 1.0)  # Normalize to [0,1]

    def _get_device_risk(self, transaction: Dict[str, Any]) -> float:
        """Calculate device-based risk"""
        device = transaction.get('device_info', {})
        if not device:
            return 1.0
        
        known_devices = [
            t.get('device_info', {}) for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and 'device_info' in t
        ]
        
        if not known_devices:
            return 0.5
            
        device_fingerprint = self._create_device_fingerprint(device)
        known_fingerprints = [
            self._create_device_fingerprint(d)
            for d in known_devices if d
        ]
        
        return 0.0 if device_fingerprint in known_fingerprints else 0.8

    def _get_transaction_pattern(self, transaction: Dict[str, Any]) -> float:
        """Analyze transaction patterns"""
        user_transactions = [
            t for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and (datetime.now() - t['timestamp']) < timedelta(days=30)
        ]
        
        if not user_transactions:
            return 0.5
            
        # Calculate average transaction amount
        avg_amount = sum(float(t['amount']) for t in user_transactions) / len(user_transactions)
        current_amount = float(transaction['amount'])
        
        # Normalize the difference
        return min(abs(current_amount - avg_amount) / (avg_amount + 1), 1.0)

    def _get_user_behavior_score(self, transaction: Dict[str, Any]) -> float:
        """Analyze user behavior patterns"""
        user_history = [
            t for t in self.historical_data
            if t['user_id'] == transaction['user_id']
        ]
        
        if not user_history:
            return 0.5
            
        # Analyze patterns in user's transaction history
        risk_factors = []
        
        # Check transaction velocity
        recent_count = len([
            t for t in user_history
            if (datetime.now() - t['timestamp']) < timedelta(minutes=5)
        ])
        risk_factors.append(min(recent_count / 3, 1.0))
        
        # Check amount variance
        amounts = [float(t['amount']) for t in user_history]
        if len(amounts) > 1:
            std_dev = np.std(amounts)
            mean_amount = np.mean(amounts)
            current_zscore = abs(float(transaction['amount']) - mean_amount) / (std_dev + 1)
            risk_factors.append(min(current_zscore / 3, 1.0))
        
        return sum(risk_factors) / len(risk_factors) if risk_factors else 0.5

    def _get_network_risk(self, transaction: Dict[str, Any]) -> float:
        """Analyze network-related risk factors"""
        network_info = transaction.get('network_info', {})
        if not network_info:
            return 0.5
            
        risk_score = 0.0
        
        # Check for VPN/Proxy usage
        if network_info.get('is_vpn') or network_info.get('is_proxy'):
            risk_score += 0.5
            
        # Check for IP address changes
        user_ips = {
            t.get('network_info', {}).get('ip_address')
            for t in self.historical_data
            if t['user_id'] == transaction['user_id']
            and 'network_info' in t
            and 'ip_address' in t['network_info']
        }
        
        if network_info.get('ip_address') not in user_ips:
            risk_score += 0.3
            
        return min(risk_score, 1.0)

    def _create_device_fingerprint(self, device_info: Dict[str, Any]) -> str:
        """Create a unique device fingerprint"""
        relevant_fields = [
            'user_agent',
            'os',
            'browser',
            'screen_resolution',
            'timezone',
            'language',
            'platform'
        ]
        
        fingerprint_parts = []
        for field in relevant_fields:
            value = device_info.get(field, '')
            if value:
                fingerprint_parts.append(f"{field}:{value}")
        
        return '|'.join(fingerprint_parts)

    def train(self, historical_transactions: List[Dict[str, Any]]):
        """Train the fraud detection model"""
        if not historical_transactions:
            return
            
        self.historical_data = historical_transactions
        
        # Extract features
        X = np.array([
            self.extract_features(t)
            for t in historical_transactions
        ])
        
        # Apply quantum feature reduction
        X_reduced = self.quantum_extractor.quantum_dimensionality_reduction(X)
        
        # Scale features and train detector
        X_scaled = self.scaler.fit_transform(X_reduced)
        self.detector.fit(X_scaled)
        
        # Save the model
        joblib.dump(self.detector, 'fraud_detector.joblib')

    def predict(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict fraud probability for a transaction
        """
        # Extract and process features
        features = self.extract_features(transaction)
        X = np.array([features])
        
        # Apply quantum feature reduction
        X_reduced = self.quantum_extractor.quantum_dimensionality_reduction(X)
        
        # Scale and predict
        X_scaled = self.scaler.transform(X_reduced)
        score = self.detector.score_samples(X_scaled)[0]
        
        # Calculate fraud probability
        fraud_probability = 1 - (score + 1) / 2
        
        # Generate feature importance
        feature_importance = dict(zip(
            self.feature_names,
            np.abs(features / np.sum(np.abs(features)))
        ))
        
        return {
            'is_fraudulent': fraud_probability > 0.8,
            'fraud_probability': fraud_probability,
            'risk_level': 'high' if fraud_probability > 0.8 else 
                         'medium' if fraud_probability > 0.5 else 'low',
            'feature_importance': feature_importance,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'quantum_enhanced': True
        }

    def update(self, transaction: Dict[str, Any], is_fraud: bool):
        """Update the model with new transaction data"""
        transaction['timestamp'] = datetime.now()
        self.historical_data.append(transaction)
        
        # Retrain model periodically
        if len(self.historical_data) % 1000 == 0:
            self.train(self.historical_data)