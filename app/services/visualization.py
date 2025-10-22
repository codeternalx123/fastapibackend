from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedVisualization:
    """Advanced visualization capabilities for analytics results"""
    
    def create_survival_plot(
        self,
        results: Dict[str, Any],
        title: str = "Survival Analysis"
    ) -> go.Figure:
        """
        Create interactive survival curve visualization
        
        Args:
            results: Survival analysis results
            title: Plot title
            
        Returns:
            go.Figure: Interactive Plotly figure
        """
        fig = go.Figure()
        
        for group, stats in results.items():
            survival_df = pd.DataFrame(stats['survival_function'])
            ci_df = pd.DataFrame(stats['confidence_intervals'])
            
            # Add survival curve
            fig.add_trace(
                go.Scatter(
                    x=survival_df.index,
                    y=survival_df.iloc[:, 0],
                    name=f"Group {group}",
                    mode='lines',
                    line=dict(width=2)
                )
            )
            
            # Add confidence intervals
            fig.add_trace(
                go.Scatter(
                    x=ci_df.index,
                    y=ci_df.iloc[:, 0],
                    fill=None,
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=ci_df.index,
                    y=ci_df.iloc[:, 1],
                    fill='tonexty',
                    mode='lines',
                    line=dict(width=0),
                    name=f"95% CI - {group}"
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Survival Probability",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_feature_importance_plot(
        self,
        importance_scores: Dict[str, float],
        title: str = "Feature Importance"
    ) -> go.Figure:
        """
        Create interactive feature importance visualization
        
        Args:
            importance_scores: Feature importance scores
            title: Plot title
            
        Returns:
            go.Figure: Interactive Plotly figure
        """
        # Sort features by importance
        sorted_features = sorted(
            importance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        features = [x[0] for x in sorted_features]
        scores = [x[1] for x in sorted_features]
        
        fig = go.Figure()
        
        # Add bar plot
        fig.add_trace(
            go.Bar(
                x=scores,
                y=features,
                orientation='h'
            )
        )
        
        # Add markers for significance thresholds
        mean_importance = np.mean(scores)
        fig.add_vline(
            x=mean_importance,
            line_dash="dash",
            annotation_text="Mean Importance"
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            template='plotly_white',
            height=max(400, len(features) * 30)
        )
        
        return fig
    
    def create_dimensionality_reduction_plot(
        self,
        reduced_data: np.ndarray,
        labels: List[str],
        method: str = "t-SNE",
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create interactive dimensionality reduction visualization
        
        Args:
            reduced_data: Reduced dimensional data
            labels: Point labels/categories
            method: Reduction method used
            title: Plot title
            
        Returns:
            go.Figure: Interactive Plotly figure
        """
        if title is None:
            title = f"{method} Visualization"
        
        df = pd.DataFrame(
            reduced_data,
            columns=['Component 1', 'Component 2']
        )
        df['Label'] = labels
        
        fig = px.scatter(
            df,
            x='Component 1',
            y='Component 2',
            color='Label',
            title=title,
            template='plotly_white'
        )
        
        fig.update_traces(
            marker=dict(size=10),
            selector=dict(mode='markers')
        )
        
        return fig
    
    def create_realtime_dashboard(
        self,
        time_series_data: pd.DataFrame,
        anomalies: Dict[str, Any]
    ) -> go.Figure:
        """
        Create interactive real-time monitoring dashboard
        
        Args:
            time_series_data: Time series data
            anomalies: Detected anomalies
            
        Returns:
            go.Figure: Interactive Plotly figure
        """
        n_metrics = len(time_series_data.columns)
        
        fig = make_subplots(
            rows=n_metrics,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=time_series_data.columns
        )
        
        for i, column in enumerate(time_series_data.columns, 1):
            # Add time series
            fig.add_trace(
                go.Scatter(
                    x=time_series_data.index,
                    y=time_series_data[column],
                    name=column,
                    mode='lines'
                ),
                row=i,
                col=1
            )
            
            # Add anomalies if detected
            if anomalies[column]['is_anomaly']:
                fig.add_trace(
                    go.Scatter(
                        x=[anomalies[column]['timestamp']],
                        y=[anomalies[column]['value']],
                        mode='markers',
                        name=f'Anomaly ({column})',
                        marker=dict(
                            size=12,
                            symbol='x',
                            color='red'
                        )
                    ),
                    row=i,
                    col=1
                )
        
        fig.update_layout(
            height=300 * n_metrics,
            title="Real-time Monitoring Dashboard",
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_prediction_dashboard(
        self,
        actual: np.ndarray,
        predicted: np.ndarray,
        intervals: Dict[str, List[float]],
        history: Dict[str, List[float]]
    ) -> List[go.Figure]:
        """
        Create interactive prediction analysis dashboard
        
        Args:
            actual: Actual values
            predicted: Predicted values
            intervals: Prediction intervals
            history: Training history
            
        Returns:
            List[go.Figure]: List of interactive Plotly figures
        """
        figures = []
        
        # Prediction vs Actual
        fig1 = go.Figure()
        
        fig1.add_trace(
            go.Scatter(
                x=actual,
                y=predicted,
                mode='markers',
                name='Predictions',
                marker=dict(size=8)
            )
        )
        
        # Add diagonal line
        max_val = max(max(actual), max(predicted))
        min_val = min(min(actual), min(predicted))
        fig1.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Perfect Prediction',
                line=dict(dash='dash')
            )
        )
        
        fig1.update_layout(
            title="Predictions vs Actual Values",
            xaxis_title="Actual Values",
            yaxis_title="Predicted Values",
            template='plotly_white'
        )
        
        figures.append(fig1)
        
        # Prediction Intervals
        fig2 = go.Figure()
        
        # Sort by actual values for better visualization
        sort_idx = np.argsort(actual)
        actual_sorted = actual[sort_idx]
        predicted_sorted = predicted[sort_idx]
        lower = np.array(intervals['lower'])[sort_idx]
        upper = np.array(intervals['upper'])[sort_idx]
        
        # Add prediction intervals
        fig2.add_trace(
            go.Scatter(
                x=np.arange(len(actual)),
                y=upper,
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=np.arange(len(actual)),
                y=lower,
                fill='tonexty',
                mode='lines',
                line=dict(width=0),
                name='95% Prediction Interval'
            )
        )
        
        # Add actual values
        fig2.add_trace(
            go.Scatter(
                x=np.arange(len(actual)),
                y=actual_sorted,
                mode='lines+markers',
                name='Actual',
                line=dict(width=2)
            )
        )
        
        fig2.update_layout(
            title="Predictions with Uncertainty",
            xaxis_title="Sample Index",
            yaxis_title="Value",
            template='plotly_white'
        )
        
        figures.append(fig2)
        
        # Training History
        fig3 = go.Figure()
        
        fig3.add_trace(
            go.Scatter(
                x=list(range(len(history['loss']))),
                y=history['loss'],
                name='Training Loss',
                mode='lines'
            )
        )
        
        if 'val_loss' in history:
            fig3.add_trace(
                go.Scatter(
                    x=list(range(len(history['val_loss']))),
                    y=history['val_loss'],
                    name='Validation Loss',
                    mode='lines'
                )
            )
        
        fig3.update_layout(
            title="Training History",
            xaxis_title="Epoch",
            yaxis_title="Loss",
            template='plotly_white'
        )
        
        figures.append(fig3)
        
        return figures