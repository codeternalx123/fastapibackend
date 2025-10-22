from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class UserExperience(BaseModel):
    """Schema for user-shared experiences"""
    id: str = Field(..., description="Unique identifier for the experience")
    user_id: str = Field(..., description="ID of the user sharing the experience")
    title: str = Field(..., description="Title of the experience")
    content: str = Field(..., description="Detailed content of the experience")
    tags: List[str] = Field(default=[], description="Tags categorizing the experience")
    treatment_phase: str = Field(..., description="Phase of treatment when experience occurred")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    helpful_count: int = Field(default=0, description="Number of users finding this helpful")
    
class InspiringQuote(BaseModel):
    """Schema for community-shared inspiring quotes"""
    id: str = Field(..., description="Unique identifier for the quote")
    user_id: str = Field(..., description="ID of the user sharing the quote")
    quote: str = Field(..., description="The inspiring quote text")
    author: Optional[str] = Field(None, description="Author of the quote if known")
    context: Optional[str] = Field(None, description="Context or situation where quote helped")
    tags: List[str] = Field(default=[], description="Tags categorizing the quote")
    created_at: datetime = Field(default_factory=datetime.now)
    resonance_count: int = Field(default=0, description="Number of users resonating with quote")

class HealingStrategy(BaseModel):
    """Schema for user-shared healing strategies"""
    id: str = Field(..., description="Unique identifier for the strategy")
    user_id: str = Field(..., description="ID of the user sharing the strategy")
    category: str = Field(..., description="Category of strategy (recipe/mindfulness/coping)")
    title: str = Field(..., description="Title of the strategy")
    description: str = Field(..., description="Detailed description of the strategy")
    instructions: List[str] = Field(..., description="Step-by-step instructions")
    effectiveness_rating: float = Field(
        ...,
        description="User-reported effectiveness (0-5)",
        ge=0,
        le=5
    )
    conditions_helped: List[str] = Field(
        ...,
        description="List of conditions this strategy helped with"
    )
    duration_minutes: Optional[int] = Field(
        None,
        description="Time needed to implement strategy"
    )
    frequency: Optional[str] = Field(
        None,
        description="How often to use this strategy"
    )
    scientific_backing: Optional[str] = Field(
        None,
        description="Any scientific research supporting this strategy"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    success_count: int = Field(
        default=0,
        description="Number of users reporting success"
    )

class CommunityInteraction(BaseModel):
    """Schema for tracking community interactions"""
    id: str = Field(..., description="Unique identifier for the interaction")
    user_id: str = Field(..., description="ID of the user interacting")
    content_id: str = Field(..., description="ID of content interacted with")
    content_type: str = Field(
        ...,
        description="Type of content (experience/quote/strategy)"
    )
    interaction_type: str = Field(
        ...,
        description="Type of interaction (view/like/save/comment)"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(
        default={},
        description="Additional metadata about interaction"
    )

class StrategyRecommendation(BaseModel):
    """Schema for strategy recommendations"""
    id: str = Field(..., description="Unique identifier for recommendation")
    user_id: str = Field(..., description="ID of user receiving recommendation")
    strategy_id: str = Field(..., description="ID of recommended strategy")
    similarity_score: float = Field(
        ...,
        description="Similarity score with user profile",
        ge=0,
        le=1
    )
    success_probability: float = Field(
        ...,
        description="Predicted probability of success",
        ge=0,
        le=1
    )
    relevance_factors: List[dict] = Field(
        ...,
        description="Factors making this relevant for user"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = Field(
        default="pending",
        description="Status of recommendation (pending/accepted/rejected)"
    )

class UserProfile(BaseModel):
    """Schema for user profile in community context"""
    id: str = Field(..., description="Unique identifier for the user")
    diagnosis: Optional[str] = Field(None, description="User's diagnosis")
    treatment_phase: Optional[str] = Field(None, description="Current treatment phase")
    age_group: Optional[str] = Field(None, description="Age group")
    preferences: dict = Field(default={}, description="User preferences")
    activity_metrics: dict = Field(
        default={},
        description="Metrics about user's community activity"
    )
    successful_strategies: List[str] = Field(
        default=[],
        description="IDs of strategies that worked for user"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CommunityInsight(BaseModel):
    """Schema for community-derived insights"""
    id: str = Field(..., description="Unique identifier for the insight")
    insight_type: str = Field(
        ...,
        description="Type of insight (correlation/trend/pattern)"
    )
    description: str = Field(..., description="Description of the insight")
    confidence_score: float = Field(
        ...,
        description="Confidence in the insight",
        ge=0,
        le=1
    )
    supporting_data: dict = Field(..., description="Data supporting this insight")
    affected_users: List[str] = Field(
        ...,
        description="User groups affected by this insight"
    )
    discovered_at: datetime = Field(default_factory=datetime.now)
    validated: bool = Field(
        default=False,
        description="Whether insight has been validated"
    )
    validation_method: Optional[str] = Field(
        None,
        description="Method used to validate insight"
    )