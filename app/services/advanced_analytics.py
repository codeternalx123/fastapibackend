from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
from lifelines import KaplanMeierFitter, CoxPHFitter
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import pandas as pd
import tensorflow as tf
from datetime import datetime, timedelta
import logging
from app.core.config import settings
from app.models.analytics_schemas import (
    SurvivalAnalysis,
    DimensionalityReduction,
    RealTimeMetrics,
    TimeToEvent
)

logger = logging.getLogger(__name__)

class AdvancedFeatures:
    """Advanced analytics features for complex analysis"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.km_fitter = KaplanMeierFitter()
        self.cox_fitter = CoxPHFitter()
        self.tsne = TSNE(n_components=2, random_state=42)

    async def survival_analysis(
        self,
        data: pd.DataFrame,
        duration_col: str,
        event_col: str,
        groups: Optional[str] = None
    ) -> SurvivalAnalysis:
        """
        Perform survival analysis on time-to-event data
        
        Args:
            data: DataFrame with survival data
            duration_col: Column name for duration
            event_col: Column name for event indicator
            groups: Optional column name for group comparison
            
        Returns:
            SurvivalAnalysis: Survival analysis results
        """
        try:
            # Fit Kaplan-Meier model
            if groups:
                results = {}
                for group in data[groups].unique():
                    mask = data[groups] == group
                    self.km_fitter.fit(
                        data.loc[mask, duration_col],
                        data.loc[mask, event_col],
                        label=str(group)
                    )
                    results[str(group)] = {
                        'survival_function': self.km_fitter.survival_function_.to_dict(),
                        'median_survival': self.km_fitter.median_survival_time_,
                        'confidence_intervals': self.km_fitter.confidence_interval_.to_dict()
                    }
            else:
                self.km_fitter.fit(
                    data[duration_col],
                    data[event_col]
                )
                results = {
                    'all': {
                        'survival_function': self.km_fitter.survival_function_.to_dict(),
                        'median_survival': self.km_fitter.median_survival_time_,
                        'confidence_intervals': self.km_fitter.confidence_interval_.to_dict()
                    }
                }
            
            # Fit Cox proportional hazards model
            covariates = [col for col in data.columns 
                         if col not in [duration_col, event_col, groups]]
            
            if covariates:
                self.cox_fitter.fit(
                    data,
                    duration_col=duration_col,
                    event_col=event_col
                )
                cox_results = {
                    'hazard_ratios': self.cox_fitter.hazard_ratios_.to_dict(),
                    'confidence_intervals': self.cox_fitter.confidence_intervals_.to_dict(),
                    'p_values': self.cox_fitter.print_summary().loc[:, 'p'].to_dict()
                }
            else:
                cox_results = None
            
            return SurvivalAnalysis(
                km_results=results,
                cox_results=cox_results
            )
            
        except Exception as e:
            logger.error(f"Survival analysis error: {str(e)}")
            raise

    async def reduce_dimensions(
        self,
        data: pd.DataFrame,
        n_components: int = 2,
        method: str = 'tsne'
    ) -> DimensionalityReduction:
        """
        Reduce data dimensionality for visualization
        
        Args:
            data: High-dimensional data
            n_components: Number of components
            method: Reduction method ('tsne', 'umap', 'pca')
            
        Returns:
            DimensionalityReduction: Reduced data and metadata
        """
        try:
            # Scale data
            scaled_data = self.scaler.fit_transform(data)
            
            # Reduce dimensions
            if method == 'tsne':
                self.tsne.n_components = n_components
                reduced_data = self.tsne.fit_transform(scaled_data)
            elif method == 'umap':
                import umap
                reducer = umap.UMAP(n_components=n_components)
                reduced_data = reducer.fit_transform(scaled_data)
            else:  # PCA
                from sklearn.decomposition import PCA
                pca = PCA(n_components=n_components)
                reduced_data = pca.fit_transform(scaled_data)
                
            # Calculate metadata
            explained_variance = None
            if method == 'pca':
                explained_variance = pca.explained_variance_ratio_.tolist()
            
            return DimensionalityReduction(
                reduced_data=reduced_data.tolist(),
                original_dims=data.shape[1],
                reduced_dims=n_components,
                method=method,
                explained_variance=explained_variance
            )
            
        except Exception as e:
            logger.error(f"Dimension reduction error: {str(e)}")
            raise

    async def analyze_real_time(
        self,
        data: pd.DataFrame,
        window_size: str = '1h'
    ) -> RealTimeMetrics:
        """
        Analyze real-time streaming metrics
        
        Args:
            data: Time series data
            window_size: Rolling window size
            
        Returns:
            RealTimeMetrics: Real-time analysis results
        """
        try:
            # Calculate rolling statistics
            rolling = data.rolling(window=window_size)
            
            results = {
                'current_values': data.iloc[-1].to_dict(),
                'rolling_mean': rolling.mean().iloc[-1].to_dict(),
                'rolling_std': rolling.std().iloc[-1].to_dict(),
                'rolling_min': rolling.min().iloc[-1].to_dict(),
                'rolling_max': rolling.max().iloc[-1].to_dict(),
                'velocity': data.diff().iloc[-1].to_dict(),
                'acceleration': data.diff().diff().iloc[-1].to_dict()
            }
            
            # Detect real-time anomalies
            anomalies = {}
            for column in data.columns:
                values = data[column]
                rolling_mean = rolling[column].mean()
                rolling_std = rolling[column].std()
                
                # Z-score based anomalies
                z_scores = abs((values - rolling_mean) / rolling_std)
                anomalies[column] = {
                    'timestamp': data.index[-1],
                    'value': float(values.iloc[-1]),
                    'z_score': float(z_scores.iloc[-1]),
                    'is_anomaly': bool(z_scores.iloc[-1] > 3)
                }
            
            return RealTimeMetrics(
                timestamp=data.index[-1],
                metrics=results,
                anomalies=anomalies
            )
            
        except Exception as e:
            logger.error(f"Real-time analysis error: {str(e)}")
            raise

    async def predict_time_to_event(
        self,
        data: pd.DataFrame,
        target_col: str,
        features: List[str],
        threshold: float
    ) -> TimeToEvent:
        """
        Predict time until specific events occur
        
        Args:
            data: Historical event data
            target_col: Column with event times
            features: Predictive features
            threshold: Event threshold
            
        Returns:
            TimeToEvent: Time-to-event predictions
        """
        try:
            # Prepare features
            X = data[features]
            y = data[target_col]
            
            # Build and train model
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=50, verbose=0)
            
            # Make predictions
            predictions = model.predict(X)
            
            # Calculate prediction intervals
            errors = predictions - y
            std_error = np.std(errors)
            
            prediction_intervals = {
                'lower': [float(p - 1.96 * std_error) for p in predictions],
                'upper': [float(p + 1.96 * std_error) for p in predictions]
            }
            
            # Calculate event probabilities
            time_windows = [1, 7, 30, 90]  # days
            probabilities = {}
            
            for window in time_windows:
                mask = y <= window
                prob = np.mean(mask)
                probabilities[f'{window}d'] = float(prob)
            
            return TimeToEvent(
                predictions=predictions.flatten().tolist(),
                intervals=prediction_intervals,
                probabilities=probabilities,
                threshold=threshold,
                features_used=features
            )
            
        except Exception as e:
            logger.error(f"Time-to-event prediction error: {str(e)}")
            raise