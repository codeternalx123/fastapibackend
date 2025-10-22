from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from ..models.meal_plan import MealPlanCreate, MealPlan
from ..core.security import get_current_user
from ..deps import get_supabase_client
from supabase import Client

router = APIRouter(prefix="/meal-plans", tags=["meal-plans"])

@router.post("", response_model=MealPlan)
async def create_meal_plan(
    meal_plan: MealPlanCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Create a new meal plan"""
    try:
        # Validate date range
        if meal_plan.end_date < meal_plan.start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        # Validate plan type and date range
        if meal_plan.plan_type == "weekly" and (meal_plan.end_date - meal_plan.start_date).days > 7:
            raise HTTPException(status_code=400, detail="Weekly plan cannot exceed 7 days")
            
        meal_plan_data = {
            **meal_plan.dict(),
            "user_id": current_user["id"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("meal_plans").insert(meal_plan_data).execute()
        
        if len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create meal plan")
            
        plan_id = result.data[0]["id"]
        
        # Create meal plan items
        meal_items = [
            {**item.dict(), "meal_plan_id": plan_id}
            for item in meal_plan.meals
        ]
        
        if meal_items:
            result = supabase.table("meal_plan_items").insert(meal_items).execute()
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[MealPlan])
async def get_meal_plans(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get all meal plans for the current user"""
    try:
        result = supabase.table("meal_plans").select("*").eq("user_id", current_user["id"]).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}", response_model=MealPlan)
async def get_meal_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get a specific meal plan"""
    try:
        result = supabase.table("meal_plans").select("*, meal_plan_items(*)").eq("id", str(plan_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal plan not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{plan_id}", response_model=MealPlan)
async def update_meal_plan(
    plan_id: UUID,
    meal_plan: MealPlanCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Update a specific meal plan"""
    try:
        # Validate date range
        if meal_plan.end_date < meal_plan.start_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        meal_plan_data = {
            **meal_plan.dict(exclude={"meals"}),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("meal_plans").update(meal_plan_data).eq("id", str(plan_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal plan not found")
            
        # Update meal plan items
        if meal_plan.meals:
            # Delete existing items
            supabase.table("meal_plan_items").delete().eq("meal_plan_id", str(plan_id)).execute()
            
            # Insert new items
            meal_items = [
                {**item.dict(), "meal_plan_id": plan_id}
                for item in meal_plan.meals
            ]
            supabase.table("meal_plan_items").insert(meal_items).execute()
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{plan_id}")
async def delete_meal_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Delete a specific meal plan"""
    try:
        # Delete meal plan items first
        supabase.table("meal_plan_items").delete().eq("meal_plan_id", str(plan_id)).execute()
        
        # Delete meal plan
        result = supabase.table("meal_plans").delete().eq("id", str(plan_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Meal plan not found")
            
        return {"message": "Meal plan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))