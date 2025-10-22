from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, IsolationForest
import tensorflow as tf
from datetime import datetime, timedelta
import logging
from app.core.config import settings
from app.services.monitoring import MetricsService
from app.models.schemas import (
    AnalyticsResult,
    MetricSummary,
    TrendAnalysis,
    Correlation,
    Forecast,
    Anomaly,
    ClusterResult,
    FeatureImportance,
    TimeSeriesDecomposition
)

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Advanced analytics and data processing system"""
    def __init__(self):
        self.metrics = MetricsService()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.nn_model = self._build_nn_model()

    def _build_nn_model(self) -> tf.keras.Model:
        """Build neural network for complex pattern detection"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        return model

    async def analyze_health_metrics(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> AnalyticsResult:
        """Comprehensive analysis of health metrics"""
        try:
            results = {}
            
            # Basic statistics
            results['summary'] = await self._calculate_metric_summary(
                data,
                metrics
            )
            
            # Trend analysis
            results['trends'] = await self._analyze_trends(
                data,
                metrics
            )
            
            # Correlations
            results['correlations'] = await self._analyze_correlations(
                data,
                metrics
            )
            
            # Forecasting
            results['forecasts'] = await self._generate_forecasts(
                data,
                metrics
            )
            
            # Anomaly detection
            results['anomalies'] = await self._detect_anomalies(
                data,
                metrics
            )
            
            # Pattern recognition
            results['patterns'] = await self._recognize_patterns(
                data,
                metrics
            )
            
            # Feature importance
            results['importance'] = await self._analyze_feature_importance(
                data,
                metrics
            )
            
            return AnalyticsResult(**results)
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            raise

    async def _calculate_metric_summary(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[MetricSummary]:
        """Calculate comprehensive statistical summaries"""
        try:
            summaries = []
            
            for metric in metrics:
                if metric not in data.columns:
                    continue
                    
                values = data[metric].dropna()
                
                # Basic statistics
                stats_summary = values.describe()
                
                # Additional statistical measures
                summary = MetricSummary(
                    metric=metric,
                    count=int(stats_summary['count']),
                    mean=float(stats_summary['mean']),
                    std=float(stats_summary['std']),
                    min=float(stats_summary['min']),
                    q1=float(stats_summary['25%']),
                    median=float(stats_summary['50%']),
                    q3=float(stats_summary['75%']),
                    max=float(stats_summary['max']),
                    skewness=float(stats.skew(values)),
                    kurtosis=float(stats.kurtosis(values)),
                    missing_ratio=float(
                        data[metric].isna().mean()
                    )
                )
                
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Summary calculation error: {str(e)}")
            raise

    async def _analyze_trends(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[TrendAnalysis]:
        """Analyze trends and patterns in metrics"""
        try:
            trends = []
            
            for metric in metrics:
                if metric not in data.columns:
                    continue
                    
                values = data[metric].dropna()
                
                # Decompose time series
                decomposition = await self._decompose_time_series(
                    values
                )
                
                # Calculate trend significance
                trend_coef = await self._calculate_trend_coefficient(
                    values
                )
                
                # Detect seasonality
                seasonal_periods = await self._detect_seasonality(
                    values
                )
                
                # Identify change points
                change_points = await self._detect_change_points(
                    values
                )
                
                trend = TrendAnalysis(
                    metric=metric,
                    direction="increasing" if trend_coef > 0 else "decreasing",
                    strength=abs(trend_coef),
                    seasonality_periods=seasonal_periods,
                    change_points=change_points,
                    decomposition=decomposition
                )
                
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analysis error: {str(e)}")
            raise

    async def _analyze_correlations(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[Correlation]:
        """Analyze correlations between metrics"""
        try:
            correlations = []
            
            # Calculate correlation matrix
            corr_matrix = data[metrics].corr()
            
            # Extract significant correlations
            for i in range(len(metrics)):
                for j in range(i + 1, len(metrics)):
                    metric1 = metrics[i]
                    metric2 = metrics[j]
                    corr_value = corr_matrix.loc[metric1, metric2]
                    
                    # Calculate p-value
                    pvalue = await self._calculate_correlation_significance(
                        data[metric1],
                        data[metric2]
                    )
                    
                    if abs(corr_value) > 0.3 and pvalue < 0.05:
                        correlation = Correlation(
                            metric1=metric1,
                            metric2=metric2,
                            coefficient=float(corr_value),
                            pvalue=float(pvalue),
                            relationship_type=self._determine_relationship_type(
                                corr_value
                            )
                        )
                        correlations.append(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Correlation analysis error: {str(e)}")
            raise

    async def _generate_forecasts(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[Forecast]:
        """Generate forecasts for metrics"""
        try:
            forecasts = []
            
            for metric in metrics:
                if metric not in data.columns:
                    continue
                    
                values = data[metric].dropna()
                
                # Train test split
                train_size = int(len(values) * 0.8)
                train = values[:train_size]
                test = values[train_size:]
                
                # Generate different forecasts
                arima_forecast = await self._generate_arima_forecast(
                    train,
                    test
                )
                prophet_forecast = await self._generate_prophet_forecast(
                    train,
                    test
                )
                nn_forecast = await self._generate_nn_forecast(
                    train,
                    test
                )
                
                # Combine forecasts (ensemble)
                ensemble_forecast = np.mean([
                    arima_forecast,
                    prophet_forecast,
                    nn_forecast
                ], axis=0)
                
                # Calculate forecast accuracy
                accuracy = self._calculate_forecast_accuracy(
                    test,
                    ensemble_forecast
                )
                
                forecast = Forecast(
                    metric=metric,
                    values=ensemble_forecast.tolist(),
                    confidence_intervals=self._calculate_confidence_intervals(
                        ensemble_forecast
                    ),
                    accuracy=accuracy
                )
                
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Forecast generation error: {str(e)}")
            raise

    async def _detect_anomalies(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[Anomaly]:
        """Detect anomalies in metrics"""
        try:
            anomalies = []
            
            for metric in metrics:
                if metric not in data.columns:
                    continue
                    
                values = data[metric].dropna()
                
                # Statistical anomaly detection
                zscore_anomalies = self._detect_zscore_anomalies(
                    values
                )
                
                # Isolation Forest anomaly detection
                if_anomalies = self._detect_if_anomalies(
                    values
                )
                
                # LOF anomaly detection
                lof_anomalies = self._detect_lof_anomalies(
                    values
                )
                
                # Combine anomaly detection results
                combined_anomalies = set(zscore_anomalies)
                combined_anomalies.update(if_anomalies)
                combined_anomalies.update(lof_anomalies)
                
                # Create anomaly objects
                for idx in combined_anomalies:
                    anomaly = Anomaly(
                        metric=metric,
                        timestamp=data.index[idx],
                        value=float(values.iloc[idx]),
                        severity=self._calculate_anomaly_severity(
                            values.iloc[idx],
                            values
                        )
                    )
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            raise

    async def _recognize_patterns(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[Dict[str, Any]]:
        """Recognize complex patterns in metrics"""
        try:
            patterns = []
            
            # Prepare features
            features = data[metrics].copy()
            features = self.scaler.fit_transform(features)
            
            # Dimensionality reduction
            pca_features = self.pca.fit_transform(features)
            
            # Clustering
            kmeans = KMeans(
                n_clusters=min(5, len(metrics)),
                random_state=42
            )
            clusters = kmeans.fit_predict(pca_features)
            
            # Pattern analysis for each cluster
            for cluster_id in range(kmeans.n_clusters):
                cluster_mask = clusters == cluster_id
                cluster_data = data[cluster_mask]
                
                pattern = {
                    'cluster_id': cluster_id,
                    'size': int(np.sum(cluster_mask)),
                    'metrics': self._analyze_cluster_metrics(
                        cluster_data,
                        metrics
                    ),
                    'temporal_patterns': self._analyze_temporal_patterns(
                        cluster_data
                    ),
                    'characteristics': self._analyze_cluster_characteristics(
                        cluster_data,
                        metrics
                    )
                }
                
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern recognition error: {str(e)}")
            raise

    async def _analyze_feature_importance(
        self,
        data: pd.DataFrame,
        metrics: List[str]
    ) -> List[FeatureImportance]:
        """Analyze feature importance"""
        try:
            importance_results = []
            
            for target in metrics:
                features = [m for m in metrics if m != target]
                X = data[features]
                y = data[target]
                
                # Random Forest importance
                self.rf_model.fit(X, y)
                rf_importance = self.rf_model.feature_importances_
                
                # Neural Network importance
                nn_importance = await self._calculate_nn_importance(
                    X,
                    y
                )
                
                # Combine importance scores
                for feature, rf_imp, nn_imp in zip(
                    features,
                    rf_importance,
                    nn_importance
                ):
                    importance = FeatureImportance(
                        target=target,
                        feature=feature,
                        importance_score=(rf_imp + nn_imp) / 2,
                        method="ensemble"
                    )
                    importance_results.append(importance)
            
            return importance_results
            
        except Exception as e:
            logger.error(f"Feature importance analysis error: {str(e)}")
            raise

    async def _decompose_time_series(
        self,
        values: pd.Series
    ) -> TimeSeriesDecomposition:
        """Decompose time series into components"""
        try:
            # Seasonal decomposition
            decomposition = sm.tsa.seasonal_decompose(
                values,
                period=self._estimate_period(values)
            )
            
            return TimeSeriesDecomposition(
                trend=decomposition.trend.tolist(),
                seasonal=decomposition.seasonal.tolist(),
                residual=decomposition.resid.tolist()
            )
            
        except Exception as e:
            logger.error(f"Time series decomposition error: {str(e)}")
            raise

    def _calculate_trend_coefficient(
        self,
        values: pd.Series
    ) -> float:
        """Calculate trend coefficient"""
        try:
            X = np.arange(len(values)).reshape(-1, 1)
            y = values.values.reshape(-1, 1)
            
            # Fit linear regression
            reg = sm.OLS(y, sm.add_constant(X)).fit()
            
            return float(reg.params[1])
            
        except Exception as e:
            logger.error(f"Trend coefficient calculation error: {str(e)}")
            return 0.0

    async def _detect_seasonality(
        self,
        values: pd.Series
    ) -> List[int]:
        """Detect seasonality periods"""
        try:
            # Calculate periodogram
            frequencies = np.fft.fft(values)
            power = np.abs(frequencies) ** 2
            
            # Find peaks in power spectrum
            peaks = np.where(
                power > np.percentile(power, 90)
            )[0]
            
            # Convert peaks to periods
            periods = [
                int(len(values) / peak) for peak in peaks
                if peak > 0 and len(values) / peak >= 2
            ]
            
            return sorted(periods)
            
        except Exception as e:
            logger.error(f"Seasonality detection error: {str(e)}")
            return []

    async def _detect_change_points(
        self,
        values: pd.Series
    ) -> List[int]:
        """Detect change points in time series"""
        try:
            # Calculate rolling statistics
            roll_mean = values.rolling(
                window=5
            ).mean()
            roll_std = values.rolling(
                window=5
            ).std()
            
            # Detect significant changes
            change_points = []
            for i in range(5, len(values)):
                if (
                    abs(values[i] - roll_mean[i]) > 2 * roll_std[i]
                    and i - len(change_points[-1:] or [0]) > 5
                ):
                    change_points.append(i)
            
            return change_points
            
        except Exception as e:
            logger.error(f"Change point detection error: {str(e)}")
            return []

    async def _calculate_correlation_significance(
        self,
        x: pd.Series,
        y: pd.Series
    ) -> float:
        """Calculate correlation significance"""
        try:
            # Calculate Pearson correlation coefficient and p-value
            correlation, pvalue = stats.pearsonr(
                x.dropna(),
                y.dropna()
            )
            
            return float(pvalue)
            
        except Exception as e:
            logger.error(
                f"Correlation significance calculation error: {str(e)}"
            )
            return 1.0

    def _determine_relationship_type(
        self,
        correlation: float
    ) -> str:
        """Determine type of relationship"""
        if correlation > 0.7:
            return "strong_positive"
        elif correlation > 0.3:
            return "moderate_positive"
        elif correlation < -0.7:
            return "strong_negative"
        elif correlation < -0.3:
            return "moderate_negative"
        else:
            return "weak"

    async def _generate_arima_forecast(
        self,
        train: pd.Series,
        test: pd.Series
    ) -> np.ndarray:
        """Generate ARIMA forecast"""
        try:
            # Fit ARIMA model
            model = sm.tsa.ARIMA(
                train,
                order=(1, 1, 1)
            ).fit()
            
            # Generate forecast
            forecast = model.forecast(
                steps=len(test)
            )
            
            return forecast.values
            
        except Exception as e:
            logger.error(f"ARIMA forecast error: {str(e)}")
            return np.zeros(len(test))

    async def _generate_prophet_forecast(
        self,
        train: pd.Series,
        test: pd.Series
    ) -> np.ndarray:
        """Generate Prophet forecast"""
        try:
            from fbprophet import Prophet
            
            # Prepare data
            df = pd.DataFrame({
                'ds': train.index,
                'y': train.values
            })
            
            # Fit model
            model = Prophet()
            model.fit(df)
            
            # Generate forecast
            future = model.make_future_dataframe(
                periods=len(test)
            )
            forecast = model.predict(future)
            
            return forecast['yhat'].values[-len(test):]
            
        except Exception as e:
            logger.error(f"Prophet forecast error: {str(e)}")
            return np.zeros(len(test))

    async def _generate_nn_forecast(
        self,
        train: pd.Series,
        test: pd.Series
    ) -> np.ndarray:
        """Generate Neural Network forecast"""
        try:
            # Prepare sequences
            X, y = self._prepare_sequences(train)
            
            # Train model
            self.nn_model.fit(
                X,
                y,
                epochs=50,
                verbose=0
            )
            
            # Generate forecast
            last_sequence = X[-1:]
            forecast = []
            
            for _ in range(len(test)):
                pred = self.nn_model.predict(
                    last_sequence
                )[0][0]
                forecast.append(pred)
                last_sequence = np.roll(
                    last_sequence,
                    -1
                )
                last_sequence[0][-1] = pred
            
            return np.array(forecast)
            
        except Exception as e:
            logger.error(f"Neural network forecast error: {str(e)}")
            return np.zeros(len(test))

    def _calculate_forecast_accuracy(
        self,
        actual: pd.Series,
        forecast: np.ndarray
    ) -> Dict[str, float]:
        """Calculate forecast accuracy metrics"""
        try:
            mse = np.mean((actual - forecast) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(actual - forecast))
            mape = np.mean(
                np.abs(
                    (actual - forecast) / actual
                )
            ) * 100
            
            return {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape)
            }
            
        except Exception as e:
            logger.error(f"Forecast accuracy calculation error: {str(e)}")
            return {
                'mse': 0.0,
                'rmse': 0.0,
                'mae': 0.0,
                'mape': 0.0
            }

    def _calculate_confidence_intervals(
        self,
        forecast: np.ndarray,
        confidence: float = 0.95
    ) -> Dict[str, List[float]]:
        """Calculate forecast confidence intervals"""
        try:
            std = np.std(forecast)
            z_score = stats.norm.ppf((1 + confidence) / 2)
            
            lower = forecast - z_score * std
            upper = forecast + z_score * std
            
            return {
                'lower': lower.tolist(),
                'upper': upper.tolist()
            }
            
        except Exception as e:
            logger.error(
                f"Confidence interval calculation error: {str(e)}"
            )
            return {
                'lower': [],
                'upper': []
            }

    def _detect_zscore_anomalies(
        self,
        values: pd.Series,
        threshold: float = 3.0
    ) -> List[int]:
        """Detect anomalies using Z-score method"""
        try:
            z_scores = np.abs(
                stats.zscore(values)
            )
            return np.where(
                z_scores > threshold
            )[0].tolist()
            
        except Exception as e:
            logger.error(f"Z-score anomaly detection error: {str(e)}")
            return []

    def _detect_if_anomalies(
        self,
        values: pd.Series
    ) -> List[int]:
        """Detect anomalies using Isolation Forest"""
        try:
            X = values.values.reshape(-1, 1)
            predictions = self.anomaly_detector.fit_predict(X)
            return np.where(
                predictions == -1
            )[0].tolist()
            
        except Exception as e:
            logger.error(
                f"Isolation Forest anomaly detection error: {str(e)}"
            )
            return []

    def _detect_lof_anomalies(
        self,
        values: pd.Series,
        contamination: float = 0.1
    ) -> List[int]:
        """Detect anomalies using Local Outlier Factor"""
        try:
            from sklearn.neighbors import LocalOutlierFactor
            
            lof = LocalOutlierFactor(
                contamination=contamination
            )
            X = values.values.reshape(-1, 1)
            predictions = lof.fit_predict(X)
            
            return np.where(
                predictions == -1
            )[0].tolist()
            
        except Exception as e:
            logger.error(f"LOF anomaly detection error: {str(e)}")
            return []

    def _calculate_anomaly_severity(
        self,
        value: float,
        values: pd.Series
    ) -> float:
        """Calculate anomaly severity score"""
        try:
            z_score = abs(
                (value - values.mean()) / values.std()
            )
            
            # Normalize to 0-1 range
            severity = 1 - np.exp(-z_score / 3)
            
            return float(severity)
            
        except Exception as e:
            logger.error(f"Anomaly severity calculation error: {str(e)}")
            return 0.0

    def _analyze_cluster_metrics(
        self,
        cluster_data: pd.DataFrame,
        metrics: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze metrics within cluster"""
        try:
            analysis = {}
            
            for metric in metrics:
                values = cluster_data[metric]
                analysis[metric] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max())
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Cluster metrics analysis error: {str(e)}")
            return {}

    def _analyze_temporal_patterns(
        self,
        cluster_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in cluster"""
        try:
            patterns = {
                'daily': self._analyze_daily_patterns(
                    cluster_data
                ),
                'weekly': self._analyze_weekly_patterns(
                    cluster_data
                ),
                'monthly': self._analyze_monthly_patterns(
                    cluster_data
                )
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Temporal pattern analysis error: {str(e)}")
            return {}

    def _analyze_cluster_characteristics(
        self,
        cluster_data: pd.DataFrame,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyze cluster characteristics"""
        try:
            characteristics = {
                'size': len(cluster_data),
                'density': self._calculate_cluster_density(
                    cluster_data[metrics]
                ),
                'cohesion': self._calculate_cluster_cohesion(
                    cluster_data[metrics]
                ),
                'separation': self._calculate_cluster_separation(
                    cluster_data[metrics]
                )
            }
            
            return characteristics
            
        except Exception as e:
            logger.error(
                f"Cluster characteristics analysis error: {str(e)}"
            )
            return {}

    async def _calculate_nn_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> np.ndarray:
        """Calculate feature importance using Neural Network"""
        try:
            # Prepare data
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.nn_model.fit(
                X_scaled,
                y,
                epochs=50,
                verbose=0
            )
            
            # Calculate importance through perturbation
            importance = []
            baseline_score = self.nn_model.evaluate(
                X_scaled,
                y,
                verbose=0
            )[0]
            
            for i in range(X.shape[1]):
                X_perturbed = X_scaled.copy()
                X_perturbed[:, i] = np.random.permutation(
                    X_perturbed[:, i]
                )
                perturbed_score = self.nn_model.evaluate(
                    X_perturbed,
                    y,
                    verbose=0
                )[0]
                importance.append(
                    perturbed_score - baseline_score
                )
            
            # Normalize importance scores
            importance = np.array(importance)
            importance = (
                importance - importance.min()
            ) / (
                importance.max() - importance.min()
            )
            
            return importance
            
        except Exception as e:
            logger.error(
                f"Neural network importance calculation error: {str(e)}"
            )
            return np.zeros(X.shape[1])