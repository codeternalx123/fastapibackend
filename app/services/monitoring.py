from typing import Dict, Any
import prometheus_client
import logging
from prometheus_client import Counter, Histogram, Gauge, Summary

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and exposing metrics"""
    def __init__(self):
        # Initialize metrics
        self.request_counter = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['endpoint', 'method', 'status']
        )
        
        self.response_time = Histogram(
            'api_response_time_seconds',
            'API response time in seconds',
            ['endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        
        self.plan_generation_time = Summary(
            'plan_generation_time_seconds',
            'Time spent generating plans'
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total number of cache hits'
        )
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total number of cache misses'
        )
        
        # ML metrics
        self.ml_prediction_time = Histogram(
            'ml_prediction_time_seconds',
            'Time spent on ML predictions',
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
        )
        self.ml_accuracy = Gauge(
            'ml_model_accuracy',
            'ML model accuracy'
        )
        
    def record_request(
        self,
        endpoint: str,
        method: str,
        status: int
    ) -> None:
        """Record an API request"""
        try:
            self.request_counter.labels(
                endpoint=endpoint,
                method=method,
                status=status
            ).inc()
            
        except Exception as e:
            logger.error(f"Metrics recording error: {str(e)}")
            
    def record_response_time(
        self,
        endpoint: str,
        duration: float
    ) -> None:
        """Record API response time"""
        try:
            self.response_time.labels(
                endpoint=endpoint
            ).observe(duration)
            
        except Exception as e:
            logger.error(f"Response time recording error: {str(e)}")
            
    def update_active_users(self, count: int) -> None:
        """Update active users count"""
        try:
            self.active_users.set(count)
            
        except Exception as e:
            logger.error(f"Active users update error: {str(e)}")
            
    @plan_generation_time.time()
    def record_plan_generation(self) -> None:
        """Record plan generation time using decorator"""
        pass
        
    def record_cache_hit(self) -> None:
        """Record cache hit"""
        try:
            self.cache_hits.inc()
            
        except Exception as e:
            logger.error(f"Cache hit recording error: {str(e)}")
            
    def record_cache_miss(self) -> None:
        """Record cache miss"""
        try:
            self.cache_misses.inc()
            
        except Exception as e:
            logger.error(f"Cache miss recording error: {str(e)}")
            
    def record_ml_prediction_time(
        self,
        duration: float
    ) -> None:
        """Record ML prediction time"""
        try:
            self.ml_prediction_time.observe(duration)
            
        except Exception as e:
            logger.error(f"ML prediction time recording error: {str(e)}")
            
    def update_ml_accuracy(self, accuracy: float) -> None:
        """Update ML model accuracy"""
        try:
            self.ml_accuracy.set(accuracy)
            
        except Exception as e:
            logger.error(f"ML accuracy update error: {str(e)}")
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        try:
            return {
                'requests': {
                    'total': self.request_counter._value.get(),
                    'by_endpoint': self._get_label_values(
                        self.request_counter,
                        'endpoint'
                    )
                },
                'response_times': {
                    'average': self.response_time.describe()[
                        'quantile'
                    ]['0.5'],
                    'p95': self.response_time.describe()[
                        'quantile'
                    ]['0.95']
                },
                'active_users': self.active_users._value.get(),
                'plan_generation': {
                    'average': self.plan_generation_time.describe()[
                        'quantile'
                    ]['0.5']
                },
                'cache': {
                    'hits': self.cache_hits._value.get(),
                    'misses': self.cache_misses._value.get(),
                    'hit_ratio': self._calculate_hit_ratio()
                },
                'ml': {
                    'accuracy': self.ml_accuracy._value.get(),
                    'avg_prediction_time': \
                        self.ml_prediction_time.describe()[
                            'quantile'
                        ]['0.5']
                }
            }
            
        except Exception as e:
            logger.error(f"Metrics retrieval error: {str(e)}")
            return {}
            
    def _get_label_values(
        self,
        metric: prometheus_client.Metric,
        label: str
    ) -> Dict[str, int]:
        """Get values for a specific label from metric"""
        try:
            values = {}
            for sample in metric.collect()[0].samples:
                if label in sample.labels:
                    values[
                        sample.labels[label]
                    ] = sample.value
            return values
            
        except Exception as e:
            logger.error(f"Label values retrieval error: {str(e)}")
            return {}
            
    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        try:
            hits = self.cache_hits._value.get()
            misses = self.cache_misses._value.get()
            total = hits + misses
            
            if total == 0:
                return 0.0
                
            return hits / total
            
        except Exception as e:
            logger.error(f"Hit ratio calculation error: {str(e)}")
            return 0.0