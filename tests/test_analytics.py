import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from app.services.analytics import AdvancedAnalytics
from app.models.analytics_schemas import (
    AnalyticsResult,
    MetricSummary,
    TrendAnalysis,
    Correlation,
    Forecast,
    Anomaly
)

@pytest.fixture
def analytics_service():
    return AdvancedAnalytics()

@pytest.fixture
def sample_data():
    # Generate sample time series data
    dates = pd.date_range(
        start='2023-01-01',
        end='2023-12-31',
        freq='D'
    )
    n = len(dates)
    
    # Generate synthetic metrics
    data = pd.DataFrame({
        'temperature': np.sin(np.linspace(0, 8*np.pi, n)) + \
                      np.random.normal(0, 0.1, n),
        'pressure': np.cos(np.linspace(0, 8*np.pi, n)) + \
                   np.random.normal(0, 0.1, n),
        'flow_rate': np.exp(np.linspace(0, 2, n)) + \
                    np.random.normal(0, 0.5, n)
    }, index=dates)
    
    return data

@pytest.mark.asyncio
async def test_analyze_health_metrics(
    analytics_service,
    sample_data
):
    """Test comprehensive health metrics analysis"""
    metrics = ['temperature', 'pressure', 'flow_rate']
    
    # Perform analysis
    results = await analytics_service.analyze_health_metrics(
        sample_data,
        metrics
    )
    
    # Validate results structure
    assert isinstance(results, AnalyticsResult)
    assert len(results.summary) == len(metrics)
    assert len(results.trends) == len(metrics)
    assert len(results.correlations) > 0
    assert len(results.forecasts) == len(metrics)
    
    # Validate metric summaries
    for summary in results.summary:
        assert isinstance(summary, MetricSummary)
        assert summary.metric in metrics
        assert summary.count > 0
        assert -1 <= summary.skewness <= 1
        assert 0 <= summary.missing_ratio <= 1

    # Validate trends
    for trend in results.trends:
        assert isinstance(trend, TrendAnalysis)
        assert trend.metric in metrics
        assert trend.direction in ['increasing', 'decreasing']
        assert 0 <= trend.strength <= 1
        
    # Validate correlations
    for corr in results.correlations:
        assert isinstance(corr, Correlation)
        assert -1 <= corr.coefficient <= 1
        assert 0 <= corr.pvalue <= 1
        
    # Validate forecasts
    for forecast in results.forecasts:
        assert isinstance(forecast, Forecast)
        assert forecast.metric in metrics
        assert len(forecast.values) > 0
        assert 'mse' in forecast.accuracy
        
    # Validate anomalies
    for anomaly in results.anomalies:
        assert isinstance(anomaly, Anomaly)
        assert anomaly.metric in metrics
        assert 0 <= anomaly.severity <= 1

@pytest.mark.asyncio
async def test_analyze_empty_data(analytics_service):
    """Test analysis with empty dataset"""
    empty_data = pd.DataFrame()
    metrics = ['temperature', 'pressure']
    
    with pytest.raises(Exception):
        await analytics_service.analyze_health_metrics(
            empty_data,
            metrics
        )

@pytest.mark.asyncio
async def test_analyze_missing_metrics(
    analytics_service,
    sample_data
):
    """Test analysis with non-existent metrics"""
    metrics = ['non_existent_metric']
    
    with pytest.raises(Exception):
        await analytics_service.analyze_health_metrics(
            sample_data,
            metrics
        )

@pytest.mark.asyncio
async def test_trend_analysis(analytics_service, sample_data):
    """Test trend analysis functionality"""
    metrics = ['temperature']
    
    # Perform analysis
    results = await analytics_service.analyze_health_metrics(
        sample_data,
        metrics
    )
    
    # Validate trend results
    trend = results.trends[0]
    assert isinstance(trend, TrendAnalysis)
    assert trend.metric == 'temperature'
    assert len(trend.seasonality_periods) > 0
    assert len(trend.change_points) >= 0
    
    # Validate decomposition
    assert len(trend.decomposition.trend) > 0
    assert len(trend.decomposition.seasonal) > 0
    assert len(trend.decomposition.residual) > 0

@pytest.mark.asyncio
async def test_anomaly_detection(analytics_service, sample_data):
    """Test anomaly detection functionality"""
    # Inject known anomalies
    sample_data.loc[
        '2023-06-15',
        'temperature'
    ] = 100  # Extreme value
    
    metrics = ['temperature']
    
    # Perform analysis
    results = await analytics_service.analyze_health_metrics(
        sample_data,
        metrics
    )
    
    # Validate anomaly detection
    anomalies = [a for a in results.anomalies
                 if a.metric == 'temperature']
    assert len(anomalies) > 0
    
    # Check if injected anomaly was detected
    detected = False
    for anomaly in anomalies:
        if anomaly.timestamp.date() == datetime(2023, 6, 15).date():
            detected = True
            assert anomaly.severity > 0.5  # High severity expected
            break
    assert detected

@pytest.mark.asyncio
async def test_correlation_analysis(analytics_service, sample_data):
    """Test correlation analysis functionality"""
    metrics = ['temperature', 'pressure']
    
    # Perform analysis
    results = await analytics_service.analyze_health_metrics(
        sample_data,
        metrics
    )
    
    # Validate correlations
    assert any(
        c.metric1 == 'temperature' and c.metric2 == 'pressure'
        for c in results.correlations
    )
    
    for corr in results.correlations:
        assert isinstance(corr, Correlation)
        assert -1 <= corr.coefficient <= 1
        assert 0 <= corr.pvalue <= 1
        assert corr.relationship_type in [
            'strong_positive',
            'moderate_positive',
            'strong_negative',
            'moderate_negative',
            'weak'
        ]

@pytest.mark.asyncio
async def test_forecasting(analytics_service, sample_data):
    """Test forecasting functionality"""
    metrics = ['temperature']
    
    # Split data for testing
    train_data = sample_data[:'2023-11-30']
    test_data = sample_data['2023-12-01':]
    
    # Perform analysis
    results = await analytics_service.analyze_health_metrics(
        train_data,
        metrics
    )
    
    # Validate forecasts
    for forecast in results.forecasts:
        assert isinstance(forecast, Forecast)
        assert len(forecast.values) > 0
        assert len(forecast.confidence_intervals['lower']) == \
               len(forecast.values)
        assert len(forecast.confidence_intervals['upper']) == \
               len(forecast.values)
        assert all(l <= u for l, u in zip(
            forecast.confidence_intervals['lower'],
            forecast.confidence_intervals['upper']
        ))
        
        # Validate accuracy metrics
        assert 'mse' in forecast.accuracy
        assert 'rmse' in forecast.accuracy
        assert 'mae' in forecast.accuracy
        assert 'mape' in forecast.accuracy
        assert all(v >= 0 for v in forecast.accuracy.values())