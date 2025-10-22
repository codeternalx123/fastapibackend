from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, date
from uuid import UUID


class NutritionalGoals(BaseModel):
    daily_calories: int
    protein_target: float
    carbs_target: float
    fats_target: float
    cancer_fighting_foods_target: int


class MealPlanItem(BaseModel):
    meal_id: UUID
    day_of_week: int = Field(ge=0, le=6)
    week_number: Optional[int] = Field(None, ge=1, le=4)
    meal_type: str
    scheduled_time: str


class MealPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    plan_type: str = Field(regex='^(weekly|monthly)$')
    nutritional_goals: NutritionalGoals
    meals: List[MealPlanItem]


class MealPlanCreate(MealPlanBase):
    pass


class MealPlan(MealPlanBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True