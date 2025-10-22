# TumorHeal Analytics API Documentation

## Overview
The TumorHeal Analytics API provides comprehensive analytics capabilities for tumor treatment data analysis. This includes survival analysis, dimensionality reduction, real-time monitoring, and predictive analytics.

## API Endpoints

### 1. Advanced Analytics
#### POST /analytics/advanced/survival
Perform survival analysis on treatment data.

**Request Body:**
```json
{
    "duration_col": "string",
    "event_col": "string",
    "groups": "string",
    "start_date": "string (YYYY-MM-DD)",
    "end_date": "string (YYYY-MM-DD)"
}
```

**Response:**
```json
{
    "km_results": {
        "group_name": {
            "survival_function": object,
            "median_survival": float,
            "confidence_intervals": object
        }
    },
    "cox_results": {
        "hazard_ratios": object,
        "confidence_intervals": object,
        "p_values": object
    }
}
```

#### POST /analytics/advanced/dimensionality
Reduce data dimensionality for visualization.

**Request Body:**
```json
{
    "features": ["string"],
    "n_components": integer,
    "method": "string (tsne|umap|pca)"
}
```

**Response:**
```json
{
    "reduced_data": array,
    "original_dims": integer,
    "reduced_dims": integer,
    "method": string,
    "explained_variance": array
}
```

#### GET /analytics/advanced/realtime
Analyze real-time streaming metrics.

**Query Parameters:**
- window_size: string (e.g., "1h", "1d")

**Response:**
```json
{
    "timestamp": string,
    "metrics": {
        "current_values": object,
        "rolling_mean": object,
        "rolling_std": object,
        "velocity": object,
        "acceleration": object
    },
    "anomalies": {
        "metric_name": {
            "timestamp": string,
            "value": float,
            "z_score": float,
            "is_anomaly": boolean
        }
    }
}
```

### 2. Feature Analysis
#### POST /analytics/features/importance
Analyze feature importance using multiple methods.

**Request Body:**
```json
{
    "target_col": "string",
    "features": ["string"]
}
```

**Response:**
```json
{
    "random_forest": {
        "feature_name": float
    },
    "correlation": {
        "feature_name": float
    },
    "permutation": {
        "feature_name": float
    },
    "ensemble": {
        "feature_name": float
    }
}
```

#### POST /analytics/features/clustering
Perform clustering analysis.

**Request Body:**
```json
{
    "features": ["string"],
    "n_clusters": integer,
    "method": "string (kmeans|dbscan)"
}
```

**Response:**
```json
{
    "labels": array,
    "centers": array,
    "n_clusters": integer,
    "cluster_stats": object,
    "separation_metrics": object
}
```

### 3. Automated Insights
#### POST /analytics/insights
Generate automated insights from data.

**Request Body:**
```json
{
    "target_col": "string"
}
```

**Response:**
```json
[
    {
        "type": "string",
        "variable": "string",
        "importance": float,
        "message": "string",
        "details": object
    }
]
```

## Best Practices

### 1. Data Preparation
- Clean missing values before analysis
- Normalize numeric features for clustering
- Handle categorical variables appropriately
- Ensure time series data is properly ordered

### 2. Performance Optimization
- Use appropriate window sizes for real-time analysis
- Limit feature set for dimensionality reduction
- Cache results when appropriate
- Use batch processing for large datasets

### 3. Model Selection
- Choose appropriate clustering method based on data structure
- Consider data size when selecting dimensionality reduction method
- Use cross-validation for predictive models
- Monitor model performance over time

### 4. Error Handling
- Validate input data types and ranges
- Handle missing or invalid values gracefully
- Provide meaningful error messages
- Implement proper logging and monitoring

## Example Usage

### Python Client
```python
import requests
import pandas as pd

# Configure client
base_url = "http://api.tumorheal.com/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Perform survival analysis
survival_data = {
    "duration_col": "treatment_duration",
    "event_col": "outcome",
    "groups": "treatment_type",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
}

response = requests.post(
    f"{base_url}/analytics/advanced/survival",
    json=survival_data,
    headers=headers
)

results = response.json()

# Generate automated insights
insights_data = {
    "target_col": "treatment_success"
}

response = requests.post(
    f"{base_url}/analytics/insights",
    json=insights_data,
    headers=headers
)

insights = response.json()

# Real-time monitoring
response = requests.get(
    f"{base_url}/analytics/advanced/realtime",
    params={"window_size": "1h"},
    headers=headers
)

metrics = response.json()
```

### Jupyter Notebook Integration
```python
from tumorheal.analytics import (
    AdvancedAnalytics,
    AdvancedVisualization
)

# Initialize analytics
analytics = AdvancedAnalytics()
viz = AdvancedVisualization()

# Perform analysis
results = await analytics.analyze_feature_importance(
    data,
    target_col="treatment_success",
    features=["age", "biomarker_1", "biomarker_2"]
)

# Create visualization
fig = viz.create_feature_importance_plot(
    results["ensemble"],
    title="Feature Importance Analysis"
)
fig.show()
```

## Troubleshooting

### Common Issues
1. Missing Data Handling
   - Symptom: Analysis fails with missing value error
   - Solution: Use data preprocessing to handle missing values

2. Performance Issues
   - Symptom: Slow response times
   - Solution: Optimize query parameters and use caching

3. Memory Errors
   - Symptom: Out of memory errors
   - Solution: Use batch processing and limit data size

4. Invalid Results
   - Symptom: Unexpected analysis results
   - Solution: Validate input data and check assumptions

### Support
For technical support or feature requests:
- Email: support@tumorheal.com
- Documentation: docs.tumorheal.com
- GitHub: github.com/tumorheal/analytics

## Release Notes

### Version 2.0.0
- Added advanced analytics features
- Enhanced visualization capabilities
- Improved performance and scalability
- Added automated insights generation
- Enhanced documentation and examples

### Version 1.0.0
- Initial release
- Basic analytics features
- Core API endpoints