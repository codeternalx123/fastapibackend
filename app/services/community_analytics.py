from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta

from app.models.community import (
    UserExperience,
    HealingStrategy,
    CommunityInsight,
    UserProfile,
    StrategyRecommendation
)

class CommunityAnalytics:
    """
    Analytics engine for processing community data and generating insights.
    """
    
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english'
        )
    
    def analyze_strategy_effectiveness(
        self,
        strategies: List[HealingStrategy],
        user_profiles: List[UserProfile]
    ) -> List[CommunityInsight]:
        """
        Analyze effectiveness of healing strategies across user segments.
        
        Args:
            strategies: List of healing strategies
            user_profiles: List of user profiles
            
        Returns:
            List of insights about strategy effectiveness
        """
        insights = []
        
        # Group strategies by category
        category_strategies = {}
        for strategy in strategies:
            if strategy.category not in category_strategies:
                category_strategies[strategy.category] = []
            category_strategies[strategy.category].append(strategy)
        
        # Analyze each category
        for category, cat_strategies in category_strategies.items():
            # Calculate average effectiveness by condition
            condition_effectiveness = {}
            condition_counts = {}
            
            for strategy in cat_strategies:
                for condition in strategy.conditions_helped:
                    if condition not in condition_effectiveness:
                        condition_effectiveness[condition] = 0
                        condition_counts[condition] = 0
                    condition_effectiveness[condition] += strategy.effectiveness_rating
                    condition_counts[condition] += 1
            
            # Generate insights for highly effective strategies
            for condition, total_score in condition_effectiveness.items():
                avg_score = total_score / condition_counts[condition]
                if avg_score >= 4.0 and condition_counts[condition] >= 10:
                    insight = CommunityInsight(
                        id=f"effectiveness_{category}_{condition}",
                        insight_type="effectiveness_pattern",
                        description=(
                            f"{category} strategies show high effectiveness "
                            f"({avg_score:.1f}/5.0) for {condition} based on "
                            f"{condition_counts[condition]} user reports"
                        ),
                        confidence_score=min(
                            condition_counts[condition] / 100,
                            0.95
                        ),
                        supporting_data={
                            "category": category,
                            "condition": condition,
                            "average_score": avg_score,
                            "sample_size": condition_counts[condition]
                        },
                        affected_users=[
                            profile.id for profile in user_profiles
                            if profile.diagnosis == condition
                        ]
                    )
                    insights.append(insight)
        
        return insights
    
    def find_strategy_correlations(
        self,
        strategies: List[HealingStrategy],
        user_profiles: List[UserProfile]
    ) -> List[CommunityInsight]:
        """
        Find correlations between different healing strategies.
        
        Args:
            strategies: List of healing strategies
            user_profiles: List of user profiles
            
        Returns:
            List of insights about strategy correlations
        """
        insights = []
        
        # Create strategy success matrix
        strategy_matrix = np.zeros((len(strategies), len(user_profiles)))
        
        for i, strategy in enumerate(strategies):
            for j, profile in enumerate(user_profiles):
                if strategy.id in profile.successful_strategies:
                    strategy_matrix[i, j] = 1
        
        # Calculate correlation matrix
        correlations = np.corrcoef(strategy_matrix)
        
        # Find highly correlated strategy pairs
        for i in range(len(strategies)):
            for j in range(i + 1, len(strategies)):
                correlation = correlations[i, j]
                if correlation >= 0.7:  # Strong positive correlation
                    # Calculate support (number of users using both)
                    support = sum(
                        1 for k in range(len(user_profiles))
                        if strategy_matrix[i, k] == 1 and strategy_matrix[j, k] == 1
                    )
                    
                    if support >= 10:  # Minimum support threshold
                        insight = CommunityInsight(
                            id=f"correlation_{strategies[i].id}_{strategies[j].id}",
                            insight_type="strategy_correlation",
                            description=(
                                f"Strong correlation ({correlation:.2f}) found between "
                                f"'{strategies[i].title}' and '{strategies[j].title}' "
                                f"based on {support} user successes"
                            ),
                            confidence_score=min(support / 100, 0.9),
                            supporting_data={
                                "strategy1_id": strategies[i].id,
                                "strategy2_id": strategies[j].id,
                                "correlation": correlation,
                                "support": support
                            },
                            affected_users=[
                                profile.id for profile in user_profiles
                                if (strategies[i].id in profile.successful_strategies or
                                    strategies[j].id in profile.successful_strategies)
                            ]
                        )
                        insights.append(insight)
        
        return insights
    
    def identify_user_clusters(
        self,
        user_profiles: List[UserProfile]
    ) -> List[CommunityInsight]:
        """
        Identify clusters of users with similar characteristics.
        
        Args:
            user_profiles: List of user profiles
            
        Returns:
            List of insights about user clusters
        """
        insights = []
        
        # Extract feature vectors from profiles
        feature_vectors = []
        for profile in user_profiles:
            vector = [
                len(profile.successful_strategies),
                len(profile.activity_metrics.get('posts', [])),
                profile.activity_metrics.get('engagement_score', 0),
                # Add more features as needed
            ]
            feature_vectors.append(vector)
        
        X = np.array(feature_vectors)
        
        # Normalize features
        X = (X - X.mean(axis=0)) / X.std(axis=0)
        
        # Perform clustering
        clustering = DBSCAN(eps=0.5, min_samples=5)
        labels = clustering.fit_predict(X)
        
        # Analyze clusters
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        for i in range(n_clusters):
            cluster_profiles = [
                profile for j, profile in enumerate(user_profiles)
                if labels[j] == i
            ]
            
            if len(cluster_profiles) >= 5:
                # Analyze cluster characteristics
                common_diagnosis = max(
                    set(p.diagnosis for p in cluster_profiles if p.diagnosis),
                    key=lambda x: sum(1 for p in cluster_profiles if p.diagnosis == x)
                )
                
                avg_strategies = np.mean([
                    len(p.successful_strategies) for p in cluster_profiles
                ])
                
                insight = CommunityInsight(
                    id=f"cluster_{i}",
                    insight_type="user_cluster",
                    description=(
                        f"Identified cluster of {len(cluster_profiles)} users "
                        f"with similar characteristics: predominantly {common_diagnosis} "
                        f"diagnosis, averaging {avg_strategies:.1f} successful strategies"
                    ),
                    confidence_score=min(len(cluster_profiles) / 50, 0.9),
                    supporting_data={
                        "cluster_size": len(cluster_profiles),
                        "common_diagnosis": common_diagnosis,
                        "avg_strategies": avg_strategies
                    },
                    affected_users=[p.id for p in cluster_profiles]
                )
                insights.append(insight)
        
        return insights
    
    def generate_strategy_recommendations(
        self,
        target_user: UserProfile,
        strategies: List[HealingStrategy],
        user_profiles: List[UserProfile],
        max_recommendations: int = 5
    ) -> List[StrategyRecommendation]:
        """
        Generate personalized strategy recommendations for a user.
        
        Args:
            target_user: User to generate recommendations for
            strategies: List of all healing strategies
            user_profiles: List of all user profiles
            max_recommendations: Maximum number of recommendations to generate
            
        Returns:
            List of strategy recommendations
        """
        recommendations = []
        
        # Find similar users
        similar_users = []
        for profile in user_profiles:
            if profile.id != target_user.id:
                # Calculate similarity score based on various factors
                similarity = 0.0
                
                # Diagnosis similarity
                if profile.diagnosis == target_user.diagnosis:
                    similarity += 0.4
                
                # Treatment phase similarity
                if profile.treatment_phase == target_user.treatment_phase:
                    similarity += 0.3
                
                # Age group similarity
                if profile.age_group == target_user.age_group:
                    similarity += 0.2
                
                # Strategy preference similarity
                common_strategies = set(profile.successful_strategies) & set(target_user.successful_strategies)
                if common_strategies:
                    similarity += 0.1 * (len(common_strategies) / len(target_user.successful_strategies))
                
                if similarity >= 0.5:  # Minimum similarity threshold
                    similar_users.append((profile, similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Find strategies that worked for similar users
        candidate_strategies = {}
        
        for similar_user, similarity in similar_users:
            for strategy_id in similar_user.successful_strategies:
                if strategy_id not in target_user.successful_strategies:
                    if strategy_id not in candidate_strategies:
                        candidate_strategies[strategy_id] = {
                            'score': 0,
                            'supporting_users': []
                        }
                    candidate_strategies[strategy_id]['score'] += similarity
                    candidate_strategies[strategy_id]['supporting_users'].append(similar_user.id)
        
        # Generate recommendations
        for strategy_id, data in sorted(
            candidate_strategies.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:max_recommendations]:
            strategy = next(s for s in strategies if s.id == strategy_id)
            
            recommendation = StrategyRecommendation(
                id=f"rec_{target_user.id}_{strategy_id}",
                user_id=target_user.id,
                strategy_id=strategy_id,
                similarity_score=min(data['score'], 1.0),
                success_probability=min(
                    len(data['supporting_users']) / len(similar_users),
                    0.95
                ),
                relevance_factors=[
                    {
                        "factor": "similar_users",
                        "count": len(data['supporting_users']),
                        "description": (
                            f"{len(data['supporting_users'])} similar users "
                            f"found this strategy helpful"
                        )
                    },
                    {
                        "factor": "diagnosis_match",
                        "value": strategy.conditions_helped,
                        "description": (
                            f"Strategy has helped users with "
                            f"{', '.join(strategy.conditions_helped)}"
                        )
                    }
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations