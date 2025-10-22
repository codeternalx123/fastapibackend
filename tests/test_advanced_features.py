import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.services.advanced_features import AdvancedAnalytics
from app.services.visualization import AdvancedVisualization

@pytest.fixture
def analytics_service():
    return AdvancedAnalytics()

@pytest.fixture
def visualization_service():
    return AdvancedVisualization()

@pytest.fixture
def feature_data():
    n_samples = 1000
    np.random.seed(42)
    
    data = pd.DataFrame({
        'feature_1': np.random.normal(0, 1, n_samples),
        'feature_2': np.random.normal(0, 1, n_samples),
        'feature_3': np.random.normal(0, 1, n_samples),
        'target': np.random.binomial(1, 0.7, n_samples)
    })
    
    # Add some structure
    data['feature_2'] = data['feature_1'] * 0.5 + np.random.normal(0, 0.1, n_samples)
    data['target'] = (data['feature_1'] + data['feature_3'] > 0).astype(int)
    
    return data

@pytest.fixture
def clustering_data():
    n_samples = 500
    np.random.seed(42)
    
    # Generate clustered data
    centers = [
        (-2, -2),
        (0, 0),
        (2, 2)
    ]
    
    data = []
    labels = []
    
    for i, (cx, cy) in enumerate(centers):
        cluster = np.random.randn(n_samples // 3, 2) * 0.5
        cluster[:, 0] += cx
        cluster[:, 1] += cy
        data.append(cluster)
        labels.extend([i] * (n_samples // 3))
    
    data = np.vstack(data)
    df = pd.DataFrame(
        data,
        columns=['x', 'y']
    )
    df['label'] = labels
    
    return df

@pytest.fixture
def time_series_data():
    dates = pd.date_range(
        start='2023-01-01',
        end='2023-12-31',
        freq='H'
    )
    
    n = len(dates)
    np.random.seed(42)
    
    data = pd.DataFrame({
        'value_1': np.sin(np.linspace(0, 8*np.pi, n)) + \
                  np.random.normal(0, 0.1, n),
        'value_2': np.cos(np.linspace(0, 8*np.pi, n)) + \
                  np.random.normal(0, 0.1, n)
    }, index=dates)
    
    return data

@pytest.mark.asyncio
async def test_feature_importance(analytics_service, feature_data):
    """Test feature importance analysis"""
    features = ['feature_1', 'feature_2', 'feature_3']
    
    results = await analytics_service.analyze_feature_importance(
        feature_data,
        'target',
        features
    )
    
    # Check results structure
    assert all(method in results for method in [
        'random_forest',
        'correlation',
        'permutation',
        'ensemble'
    ])
    
    # Check score normalization
    for method, scores in results.items():
        assert all(0 <= score <= 1 for score in scores.values())
        assert len(scores) == len(features)
        
    # Verify feature 1 and 3 are most important
    ensemble_scores = results['ensemble']
    assert ensemble_scores['feature_1'] > 0.5
    assert ensemble_scores['feature_3'] > 0.5
    assert ensemble_scores['feature_2'] < ensemble_scores['feature_1']

@pytest.mark.asyncio
async def test_clustering(analytics_service, clustering_data):
    """Test clustering analysis"""
    features = ['x', 'y']
    
    # Test KMeans
    kmeans_results = await analytics_service.perform_clustering(
        clustering_data,
        features,
        n_clusters=3,
        method='kmeans'
    )
    
    assert 'labels' in kmeans_results
    assert 'centers' in kmeans_results
    assert 'cluster_stats' in kmeans_results
    assert 'separation_metrics' in kmeans_results
    
    # Check cluster count
    assert len(set(kmeans_results['labels'])) == 3
    
    # Verify separation metrics
    assert kmeans_results['separation_metrics']['silhouette'] > 0.5
    
    # Test DBSCAN
    dbscan_results = await analytics_service.perform_clustering(
        clustering_data,
        features,
        method='dbscan'
    )
    
    assert 'labels' in dbscan_results
    assert 'n_clusters' in dbscan_results
    assert dbscan_results['n_clusters'] >= 2

@pytest.mark.asyncio
async def test_automated_insights(analytics_service, feature_data):
    """Test automated insight generation"""
    insights = await analytics_service.generate_automated_insights(
        feature_data,
        'target'
    )
    
    # Check insights structure
    assert len(insights) > 0
    for insight in insights:
        assert 'type' in insight
        assert 'importance' in insight
        assert 'message' in insight
        assert 0 <= insight['importance'] <= 1
    
    # Verify correlation insights
    correlation_insights = [
        i for i in insights
        if i['type'] == 'correlation'
    ]
    assert any(
        i['variables'] == ['feature_1', 'feature_2']
        for i in correlation_insights
    )
    
    # Check target relationship insights
    target_insights = [
        i for i in insights
        if i['type'] == 'target_relationship'
    ]
    assert len(target_insights) > 0

@pytest.mark.asyncio
async def test_visualization(
    visualization_service,
    feature_data,
    clustering_data,
    time_series_data
):
    """Test visualization capabilities"""
    # Test feature importance plot
    importance_scores = {
        'feature_1': 0.8,
        'feature_2': 0.3,
        'feature_3': 0.6
    }
    
    fig = visualization_service.create_feature_importance_plot(
        importance_scores
    )
    assert fig is not None
    
    # Test dimensionality reduction plot
    reduced_data = np.random.randn(100, 2)
    labels = ['A'] * 50 + ['B'] * 50
    
    fig = visualization_service.create_dimensionality_reduction_plot(
        reduced_data,
        labels
    )
    assert fig is not None
    
    # Test real-time dashboard
    anomalies = {
        'value_1': {
            'timestamp': time_series_data.index[-1],
            'value': time_series_data['value_1'].iloc[-1],
            'z_score': 2.5,
            'is_anomaly': False
        },
        'value_2': {
            'timestamp': time_series_data.index[-1],
            'value': time_series_data['value_2'].iloc[-1],
            'z_score': 3.5,
            'is_anomaly': True
        }
    }
    
    fig = visualization_service.create_realtime_dashboard(
        time_series_data,
        anomalies
    )
    assert fig is not None

@pytest.mark.asyncio
async def test_error_handling(analytics_service):
    """Test error handling"""
    # Test empty data
    empty_data = pd.DataFrame()
    
    with pytest.raises(Exception):
        await analytics_service.analyze_feature_importance(
            empty_data,
            'target',
            ['feature']
        )
    
    with pytest.raises(Exception):
        await analytics_service.perform_clustering(
            empty_data,
            ['x', 'y']
        )
    
    # Test invalid inputs
    invalid_data = pd.DataFrame({
        'feature': ['a', 'b', 'c'],
        'target': [1, 2, 3]
    })
    
    with pytest.raises(Exception):
        await analytics_service.analyze_feature_importance(
            invalid_data,
            'target',
            ['feature']
        )

@pytest.mark.asyncio
async def test_performance(analytics_service):
    """Test performance with large datasets"""
    # Generate large dataset
    n_samples = 10000
    n_features = 50
    
    large_data = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    large_data['target'] = np.random.randint(0, 2, n_samples)
    
    # Test feature importance performance
    start_time = datetime.now()
    
    results = await analytics_service.analyze_feature_importance(
        large_data,
        'target',
        [f'feature_{i}' for i in range(n_features)]
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    assert duration < 30  # Should complete within 30 seconds
    
    # Test clustering performance
    start_time = datetime.now()
    
    results = await analytics_service.perform_clustering(
        large_data,
        [f'feature_{i}' for i in range(5)]  # Use first 5 features
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    assert duration < 30  # Should complete within 30 seconds