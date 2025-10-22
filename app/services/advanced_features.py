from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    IsolationForest
)
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    """Advanced analytics features for deeper insights"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.rf_regressor = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
    
    async def analyze_feature_importance(
        self,
        data: pd.DataFrame,
        target_col: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze feature importance using multiple methods
        
        Args:
            data: Input data
            target_col: Target variable
            features: Feature columns
            
        Returns:
            Dict with importance scores and rankings
        """
        try:
            X = data[features]
            y = data[target_col]
            
            results = {}
            
            # Random Forest importance
            if y.dtype in ['int64', 'bool']:
                self.rf_classifier.fit(X, y)
                rf_importance = self.rf_classifier.feature_importances_
            else:
                self.rf_regressor.fit(X, y)
                rf_importance = self.rf_regressor.feature_importances_
                
            # Correlation importance
            corr_importance = np.abs([
                stats.pearsonr(X[f], y)[0] for f in features
            ])
            
            # Permutation importance
            perm_importance = []
            baseline_score = self.rf_regressor.score(X, y)
            
            for feature in features:
                X_perm = X.copy()
                X_perm[feature] = np.random.permutation(X_perm[feature])
                perm_score = self.rf_regressor.score(X_perm, y)
                perm_importance.append(baseline_score - perm_score)
            
            # Combine and normalize scores
            results['random_forest'] = self._normalize_scores(
                dict(zip(features, rf_importance))
            )
            results['correlation'] = self._normalize_scores(
                dict(zip(features, corr_importance))
            )
            results['permutation'] = self._normalize_scores(
                dict(zip(features, perm_importance))
            )
            
            # Calculate ensemble importance
            ensemble_scores = {}
            for feature in features:
                ensemble_scores[feature] = np.mean([
                    results['random_forest'][feature],
                    results['correlation'][feature],
                    results['permutation'][feature]
                ])
                
            results['ensemble'] = self._normalize_scores(ensemble_scores)
            
            return results
            
        except Exception as e:
            logger.error(f"Feature importance analysis error: {str(e)}")
            raise
    
    async def perform_clustering(
        self,
        data: pd.DataFrame,
        features: List[str],
        n_clusters: Optional[int] = None,
        method: str = 'kmeans'
    ) -> Dict[str, Any]:
        """
        Perform clustering analysis using multiple methods
        
        Args:
            data: Input data
            features: Feature columns
            n_clusters: Number of clusters (for KMeans)
            method: Clustering method
            
        Returns:
            Dict with clustering results
        """
        try:
            X = self.scaler.fit_transform(data[features])
            results = {}
            
            if method == 'kmeans':
                if n_clusters is None:
                    n_clusters = self._estimate_optimal_clusters(X)
                
                kmeans = KMeans(
                    n_clusters=n_clusters,
                    random_state=42
                )
                clusters = kmeans.fit_predict(X)
                
                results['labels'] = clusters
                results['centers'] = kmeans.cluster_centers_
                results['inertia'] = kmeans.inertia_
                results['n_clusters'] = n_clusters
                
            else:  # DBSCAN
                dbscan = DBSCAN(eps=0.5, min_samples=5)
                clusters = dbscan.fit_predict(X)
                
                results['labels'] = clusters
                results['n_clusters'] = len(set(clusters)) - (1 if -1 in clusters else 0)
                results['noise_points'] = np.sum(clusters == -1)
            
            # Calculate cluster stats
            results['cluster_stats'] = self._calculate_cluster_stats(
                data[features],
                clusters
            )
            
            # Analyze cluster separation
            results['separation_metrics'] = self._analyze_cluster_separation(
                X,
                clusters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Clustering analysis error: {str(e)}")
            raise
    
    async def generate_automated_insights(
        self,
        data: pd.DataFrame,
        target_col: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate automated insights from data
        
        Args:
            data: Input data
            target_col: Optional target variable
            
        Returns:
            List of insights
        """
        try:
            insights = []
            
            # Distribution analysis
            for column in data.columns:
                if pd.api.types.is_numeric_dtype(data[column]):
                    insight = self._analyze_distribution(
                        data[column],
                        column
                    )
                    insights.append(insight)
            
            # Correlation analysis
            if len(data.select_dtypes(include=[np.number]).columns) > 1:
                corr_insights = self._analyze_correlations(data)
                insights.extend(corr_insights)
            
            # Time-based patterns
            time_cols = data.select_dtypes(
                include=['datetime64']
            ).columns
            
            for col in time_cols:
                time_insights = self._analyze_temporal_patterns(
                    data,
                    col
                )
                insights.extend(time_insights)
            
            # Target-specific insights
            if target_col:
                target_insights = self._analyze_target_relationships(
                    data,
                    target_col
                )
                insights.extend(target_insights)
            
            # Sort insights by importance
            insights.sort(key=lambda x: x['importance'], reverse=True)
            
            return insights
            
        except Exception as e:
            logger.error(f"Automated insight generation error: {str(e)}")
            raise
    
    def _normalize_scores(
        self,
        scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Normalize scores to [0, 1] range"""
        values = np.array(list(scores.values()))
        min_val = np.min(values)
        max_val = np.max(values)
        
        if max_val == min_val:
            return {k: 1.0 for k in scores}
        
        return {
            k: (v - min_val) / (max_val - min_val)
            for k, v in scores.items()
        }
    
    def _estimate_optimal_clusters(
        self,
        X: np.ndarray,
        max_clusters: int = 10
    ) -> int:
        """Estimate optimal number of clusters using elbow method"""
        inertias = []
        
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
        
        # Calculate elbow point
        diffs = np.diff(inertias)
        elbow_point = np.argmax(diffs) + 1
        
        return elbow_point
    
    def _calculate_cluster_stats(
        self,
        data: pd.DataFrame,
        labels: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate statistics for each cluster"""
        stats = {}
        
        for cluster in set(labels):
            if cluster == -1:  # Noise points in DBSCAN
                continue
                
            cluster_data = data[labels == cluster]
            
            stats[f'cluster_{cluster}'] = {
                'size': len(cluster_data),
                'mean': cluster_data.mean().to_dict(),
                'std': cluster_data.std().to_dict(),
                'min': cluster_data.min().to_dict(),
                'max': cluster_data.max().to_dict()
            }
        
        return stats
    
    def _analyze_cluster_separation(
        self,
        X: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, float]:
        """Analyze cluster separation metrics"""
        metrics = {}
        
        # Silhouette score
        from sklearn.metrics import silhouette_score
        if len(set(labels)) > 1:
            metrics['silhouette'] = float(
                silhouette_score(X, labels)
            )
        
        # Calinski-Harabasz score
        from sklearn.metrics import calinski_harabasz_score
        metrics['calinski_harabasz'] = float(
            calinski_harabasz_score(X, labels)
        )
        
        # Davies-Bouldin score
        from sklearn.metrics import davies_bouldin_score
        metrics['davies_bouldin'] = float(
            davies_bouldin_score(X, labels)
        )
        
        return metrics
    
    def _analyze_distribution(
        self,
        series: pd.Series,
        column: str
    ) -> Dict[str, Any]:
        """Analyze distribution of a variable"""
        insight = {
            'type': 'distribution',
            'variable': column,
            'importance': 0.0
        }
        
        # Basic statistics
        stats_dict = series.describe().to_dict()
        skewness = stats.skew(series.dropna())
        kurtosis = stats.kurtosis(series.dropna())
        
        # Test for normality
        _, normality_pvalue = stats.normaltest(
            series.dropna()
        )
        
        # Detect outliers
        z_scores = np.abs(stats.zscore(series.dropna()))
        outliers = np.sum(z_scores > 3)
        
        insight['statistics'] = {
            **stats_dict,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'outliers': outliers
        }
        
        # Generate textual insights
        messages = []
        
        if abs(skewness) > 1:
            messages.append(
                f"Distribution is {'positively' if skewness > 0 else 'negatively'} skewed"
            )
            insight['importance'] = max(
                insight['importance'],
                abs(skewness) / 2
            )
        
        if outliers > 0:
            messages.append(
                f"Found {outliers} potential outliers"
            )
            insight['importance'] = max(
                insight['importance'],
                min(outliers / len(series), 0.8)
            )
        
        if normality_pvalue < 0.05:
            messages.append(
                "Distribution significantly deviates from normal"
            )
            insight['importance'] = max(
                insight['importance'],
                0.7
            )
        
        insight['messages'] = messages
        
        return insight
    
    def _analyze_correlations(
        self,
        data: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Analyze correlations between variables"""
        insights = []
        
        # Calculate correlation matrix
        corr_matrix = data.corr()
        
        # Find significant correlations
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr = corr_matrix.iloc[i, j]
                
                if abs(corr) > 0.7:
                    insight = {
                        'type': 'correlation',
                        'variables': [
                            corr_matrix.columns[i],
                            corr_matrix.columns[j]
                        ],
                        'correlation': corr,
                        'importance': abs(corr)
                    }
                    
                    insight['message'] = (
                        f"Strong {'positive' if corr > 0 else 'negative'} "
                        f"correlation ({corr:.2f}) between "
                        f"{insight['variables'][0]} and {insight['variables'][1]}"
                    )
                    
                    insights.append(insight)
        
        return insights
    
    def _analyze_temporal_patterns(
        self,
        data: pd.DataFrame,
        time_col: str
    ) -> List[Dict[str, Any]]:
        """Analyze temporal patterns in data"""
        insights = []
        
        # Extract time components
        time_data = pd.DataFrame({
            'hour': data[time_col].dt.hour,
            'day': data[time_col].dt.day,
            'month': data[time_col].dt.month,
            'year': data[time_col].dt.year
        })
        
        # Analyze patterns for each numeric column
        for col in data.select_dtypes(include=[np.number]).columns:
            if col == time_col:
                continue
                
            # Check for daily patterns
            hourly_means = data.groupby(
                time_data['hour']
            )[col].mean()
            hourly_std = hourly_means.std()
            
            if hourly_std > 0.1 * hourly_means.mean():
                insights.append({
                    'type': 'temporal',
                    'variable': col,
                    'pattern': 'daily',
                    'importance': min(
                        hourly_std / hourly_means.mean(),
                        0.9
                    ),
                    'message': (
                        f"Strong daily pattern detected in {col}"
                    )
                })
            
            # Check for monthly patterns
            monthly_means = data.groupby(
                time_data['month']
            )[col].mean()
            monthly_std = monthly_means.std()
            
            if monthly_std > 0.1 * monthly_means.mean():
                insights.append({
                    'type': 'temporal',
                    'variable': col,
                    'pattern': 'monthly',
                    'importance': min(
                        monthly_std / monthly_means.mean(),
                        0.8
                    ),
                    'message': (
                        f"Monthly seasonality detected in {col}"
                    )
                })
        
        return insights
    
    def _analyze_target_relationships(
        self,
        data: pd.DataFrame,
        target_col: str
    ) -> List[Dict[str, Any]]:
        """Analyze relationships with target variable"""
        insights = []
        target = data[target_col]
        
        for col in data.select_dtypes(include=[np.number]).columns:
            if col == target_col:
                continue
            
            # Calculate correlation
            corr, pvalue = stats.pearsonr(
                data[col].fillna(0),
                target.fillna(0)
            )
            
            if abs(corr) > 0.3 and pvalue < 0.05:
                insights.append({
                    'type': 'target_relationship',
                    'variable': col,
                    'correlation': corr,
                    'pvalue': pvalue,
                    'importance': abs(corr),
                    'message': (
                        f"Significant relationship detected between "
                        f"{col} and target variable (corr={corr:.2f})"
                    )
                })
        
        return insights