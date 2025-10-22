from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class NutritionInfo(BaseModel):
    calories: int
    protein: float
    carbs: float
    fats: float
    nutrients: Dict = Field(default_factory=dict)


class MealBase(BaseModel):
    name: str
    description: Optional[str] = None
    meal_type: str
    calories: int
    protein: float
    carbs: float
    fats: float
    nutrients: Dict = Field(default_factory=dict)
    cancer_fighting_ingredients: List[str] = Field(default_factory=list)
    consumed_at: datetime = Field(default_factory=datetime.now)


class MealCreate(MealBase):
    pass


class Meal(MealBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class MealSummary(BaseModel):
    total_meals: int
    average_calories: float
    nutritional_goals_met: bool
    cancer_fighting_foods_consumed: int