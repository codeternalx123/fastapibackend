import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.services.advanced_analytics import AdvancedFeatures
from app.models.analytics_schemas import (
    SurvivalAnalysis,
    DimensionalityReduction,
    RealTimeMetrics,
    TimeToEvent
)

@pytest.fixture
def advanced_analytics():
    return AdvancedFeatures()

@pytest.fixture
def survival_data():
    # Generate sample survival data
    n = 1000
    np.random.seed(42)
    
    data = pd.DataFrame({
        'duration': np.random.exponential(50, n),
        'event': np.random.binomial(1, 0.7, n),
        'age': np.random.normal(60, 10, n),
        'treatment': np.random.choice(['A', 'B', 'C'], n),
        'stage': np.random.choice(['I', 'II', 'III'], n)
    })
    
    return data

@pytest.fixture
def realtime_data():
    # Generate sample real-time data
    dates = pd.date_range(
        start='2023-01-01',
        end='2023-01-02',
        freq='1min'
    )
    
    n = len(dates)
    data = pd.DataFrame({
        'temperature': np.sin(np.linspace(0, 8*np.pi, n)) + \
                      np.random.normal(0, 0.1, n),
        'pressure': np.cos(np.linspace(0, 8*np.pi, n)) + \
                   np.random.normal(0, 0.1, n),
        'flow_rate': np.exp(np.linspace(0, 2, n)) + \
                    np.random.normal(0, 0.5, n)
    }, index=dates)
    
    return data

@pytest.fixture
def event_data():
    # Generate sample event data
    n = 500
    np.random.seed(42)
    
    data = pd.DataFrame({
        'time_to_event': np.random.exponential(30, n),
        'biomarker_1': np.random.normal(100, 15, n),
        'biomarker_2': np.random.normal(5, 1, n),
        'age': np.random.normal(60, 10, n),
        'treatment_duration': np.random.uniform(10, 90, n)
    })
    
    return data

@pytest.mark.asyncio
async def test_survival_analysis(advanced_analytics, survival_data):
    """Test survival analysis functionality"""
    # Test without groups
    results = await advanced_analytics.survival_analysis(
        survival_data,
        'duration',
        'event'
    )
    
    assert isinstance(results, SurvivalAnalysis)
    assert 'all' in results.km_results
    assert results.km_results['all']['median_survival'] > 0
    
    # Test with groups
    results = await advanced_analytics.survival_analysis(
        survival_data,
        'duration',
        'event',
        'treatment'
    )
    
    assert all(g in results.km_results for g in ['A', 'B', 'C'])
    assert results.cox_results is not None
    assert 'age' in results.cox_results['hazard_ratios']

@pytest.mark.asyncio
async def test_dimensionality_reduction(advanced_analytics, survival_data):
    """Test dimensionality reduction methods"""
    features = ['age', 'duration']
    data = survival_data[features]
    
    # Test t-SNE
    results = await advanced_analytics.reduce_dimensions(
        data,
        n_components=2,
        method='tsne'
    )
    
    assert isinstance(results, DimensionalityReduction)
    assert len(results.reduced_data) == len(data)
    assert len(results.reduced_data[0]) == 2
    assert results.method == 'tsne'
    
    # Test PCA
    results = await advanced_analytics.reduce_dimensions(
        data,
        n_components=2,
        method='pca'
    )
    
    assert results.method == 'pca'
    assert results.explained_variance is not None
    assert len(results.explained_variance) == 2

@pytest.mark.asyncio
async def test_realtime_analysis(advanced_analytics, realtime_data):
    """Test real-time analytics functionality"""
    results = await advanced_analytics.analyze_real_time(
        realtime_data,
        window_size='10min'
    )
    
    assert isinstance(results, RealTimeMetrics)
    assert isinstance(results.timestamp, pd.Timestamp)
    
    # Check metrics
    assert all(m in results.metrics for m in [
        'current_values',
        'rolling_mean',
        'rolling_std',
        'velocity',
        'acceleration'
    ])
    
    # Check anomalies
    for metric in realtime_data.columns:
        assert metric in results.anomalies
        assert 'is_anomaly' in results.anomalies[metric]
        assert isinstance(
            results.anomalies[metric]['is_anomaly'],
            bool
        )

@pytest.mark.asyncio
async def test_time_to_event_prediction(advanced_analytics, event_data):
    """Test time-to-event prediction functionality"""
    features = ['biomarker_1', 'biomarker_2', 'age']
    
    results = await advanced_analytics.predict_time_to_event(
        event_data,
        'time_to_event',
        features,
        threshold=30
    )
    
    assert isinstance(results, TimeToEvent)
    assert len(results.predictions) == len(event_data)
    assert all(f in results.features_used for f in features)
    
    # Check prediction intervals
    assert 'lower' in results.intervals
    assert 'upper' in results.intervals
    assert len(results.intervals['lower']) == len(event_data)
    assert all(
        l <= u for l, u in zip(
            results.intervals['lower'],
            results.intervals['upper']
        )
    )
    
    # Check probabilities
    assert '30d' in results.probabilities
    assert 0 <= results.probabilities['30d'] <= 1

@pytest.mark.asyncio
async def test_error_handling(advanced_analytics):
    """Test error handling in analytics functions"""
    # Test with empty data
    empty_data = pd.DataFrame()
    
    with pytest.raises(Exception):
        await advanced_analytics.survival_analysis(
            empty_data,
            'duration',
            'event'
        )
    
    with pytest.raises(Exception):
        await advanced_analytics.reduce_dimensions(
            empty_data
        )
    
    with pytest.raises(Exception):
        await advanced_analytics.analyze_real_time(
            empty_data
        )
    
    with pytest.raises(Exception):
        await advanced_analytics.predict_time_to_event(
            empty_data,
            'time',
            ['feature'],
            30
        )

@pytest.mark.asyncio
async def test_large_dataset_performance(advanced_analytics):
    """Test performance with large datasets"""
    # Generate large dataset
    n = 10000
    large_data = pd.DataFrame({
        'time': np.random.exponential(50, n),
        'event': np.random.binomial(1, 0.7, n),
        'feature1': np.random.normal(0, 1, n),
        'feature2': np.random.normal(0, 1, n),
        'feature3': np.random.normal(0, 1, n)
    })
    
    # Test survival analysis performance
    start_time = datetime.now()
    results = await advanced_analytics.survival_analysis(
        large_data,
        'time',
        'event'
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    assert duration < 10  # Should complete within 10 seconds
    assert isinstance(results, SurvivalAnalysis)
    
    # Test dimensionality reduction performance
    features = ['feature1', 'feature2', 'feature3']
    start_time = datetime.now()
    results = await advanced_analytics.reduce_dimensions(
        large_data[features]
    )
    duration = (datetime.now() - start_time).total_seconds()
    
    assert duration < 30  # Should complete within 30 seconds
    assert isinstance(results, DimensionalityReduction)

@pytest.mark.asyncio
async def test_edge_cases(advanced_analytics, survival_data):
    """Test edge cases and boundary conditions"""
    # Test with single sample
    single_sample = survival_data.iloc[:1]
    
    with pytest.raises(Exception):
        await advanced_analytics.survival_analysis(
            single_sample,
            'duration',
            'event'
        )
    
    # Test with constant values
    constant_data = pd.DataFrame({
        'feature': [1] * 100
    })
    
    with pytest.raises(Exception):
        await advanced_analytics.reduce_dimensions(
            constant_data
        )
    
    # Test with missing values
    survival_data.loc[0, 'duration'] = np.nan
    
    with pytest.raises(Exception):
        await advanced_analytics.survival_analysis(
            survival_data,
            'duration',
            'event'
        )