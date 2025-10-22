from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from ..models.meal import MealCreate, Meal, MealSummary
from ..core.security import get_current_user
from ..deps import get_supabase_client
from supabase import Client, create_client

router = APIRouter(prefix="/meals", tags=["meals"])

@router.post("/log", response_model=Meal)
async def log_meal(
    meal: MealCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Log a new meal with nutritional information"""
    try:
        meal_data = {
            **meal.dict(),
            "user_id": current_user["id"],
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("meals").insert(meal_data).execute()
        
        if len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create meal")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=dict)
async def get_meal_history(
    start_date: date,
    end_date: date,
    meal_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get meal history for a specified date range"""
    try:
        query = supabase.table("meals").select("*").eq("user_id", current_user["id"])
        
        # Add date range filter
        query = query.gte("consumed_at", start_date.isoformat())
        query = query.lte("consumed_at", end_date.isoformat())
        
        # Add meal type filter if specified
        if meal_type:
            query = query.eq("meal_type", meal_type)
            
        result = query.execute()
        
        if not result.data:
            return {
                "meals": [],
                "summary": {
                    "total_meals": 0,
                    "average_calories": 0,
                    "nutritional_goals_met": False,
                    "cancer_fighting_foods_consumed": 0
                }
            }
            
        meals = result.data
        
        # Calculate summary statistics
        total_meals = len(meals)
        avg_calories = sum(meal["calories"] for meal in meals) / total_meals
        cancer_fighting_foods = sum(len(meal["cancer_fighting_ingredients"]) for meal in meals)
        
        # Basic nutritional goals check (can be customized based on user's needs)
        nutritional_goals_met = avg_calories >= 1500 and avg_calories <= 2500
        
        summary = MealSummary(
            total_meals=total_meals,
            average_calories=avg_calories,
            nutritional_goals_met=nutritional_goals_met,
            cancer_fighting_foods_consumed=cancer_fighting_foods
        )
        
        return {
            "meals": meals,
            "summary": summary.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meal_id}", response_model=Meal)
async def get_meal(
    meal_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get details of a specific meal"""
    try:
        result = supabase.table("meals").select("*").eq("id", str(meal_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Delete a specific meal"""
    try:
        result = supabase.table("meals").delete().eq("id", str(meal_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal not found")
            
        return {"message": "Meal deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{meal_id}", response_model=Meal)
async def update_meal(
    meal_id: UUID,
    meal: MealCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Update a specific meal"""
    try:
        result = supabase.table("meals").update(meal.dict()).eq("id", str(meal_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))