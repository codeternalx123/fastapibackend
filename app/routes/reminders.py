from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from ..models.reminder import ReminderCreate, Reminder
from ..core.security import get_current_user
from ..deps import get_supabase_client, redis
from supabase import Client
import json

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("", response_model=Reminder)
async def create_reminder(
    reminder: ReminderCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Create a new reminder"""
    try:
        # Validate days of week
        if reminder.days_of_week:
            if not all(0 <= day <= 6 for day in reminder.days_of_week):
                raise HTTPException(status_code=400, detail="Days must be between 0 and 6")
                
        reminder_data = {
            **reminder.dict(),
            "user_id": current_user["id"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("reminders").insert(reminder_data).execute()
        
        if len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create reminder")
            
        # Store reminder in Redis for quick access
        reminder_id = result.data[0]["id"]
        redis_key = f"reminder:{current_user['id']}:{reminder_id}"
        redis.setex(
            redis_key,
            60 * 60 * 24,  # 24 hour expiry
            json.dumps(result.data[0])
        )
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Reminder])
async def get_reminders(
    reminder_type: Optional[str] = None,
    active_only: bool = False,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get all reminders for the current user"""
    try:
        query = supabase.table("reminders").select("*").eq("user_id", current_user["id"])
        
        if reminder_type:
            query = query.eq("reminder_type", reminder_type)
            
        if active_only:
            query = query.eq("is_active", True)
            
        result = query.execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(
    reminder_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Get a specific reminder"""
    try:
        # Try to get from Redis first
        redis_key = f"reminder:{current_user['id']}:{reminder_id}"
        cached_reminder = redis.get(redis_key)
        
        if cached_reminder:
            return json.loads(cached_reminder)
            
        result = supabase.table("reminders").select("*").eq("id", str(reminder_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Reminder not found")
            
        # Cache the result
        redis.setex(
            redis_key,
            60 * 60 * 24,  # 24 hour expiry
            json.dumps(result.data[0])
        )
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(
    reminder_id: UUID,
    reminder: ReminderCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Update a specific reminder"""
    try:
        # Validate days of week
        if reminder.days_of_week:
            if not all(0 <= day <= 6 for day in reminder.days_of_week):
                raise HTTPException(status_code=400, detail="Days must be between 0 and 6")

        reminder_data = {
            **reminder.dict(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("reminders").update(reminder_data).eq("id", str(reminder_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Reminder not found")
            
        # Update Redis cache
        redis_key = f"reminder:{current_user['id']}:{reminder_id}"
        redis.setex(
            redis_key,
            60 * 60 * 24,  # 24 hour expiry
            json.dumps(result.data[0])
        )
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Delete a specific reminder"""
    try:
        result = supabase.table("reminders").delete().eq("id", str(reminder_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Reminder not found")
            
        # Remove from Redis cache
        redis_key = f"reminder:{current_user['id']}:{reminder_id}"
        redis.delete(redis_key)
            
        return {"message": "Reminder deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reminder_id}/toggle", response_model=Reminder)
async def toggle_reminder(
    reminder_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Toggle a reminder's active status"""
    try:
        # Get current status
        result = supabase.table("reminders").select("is_active").eq("id", str(reminder_id)).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Reminder not found")
            
        current_status = result.data[0]["is_active"]
        
        # Toggle status
        result = supabase.table("reminders").update(
            {"is_active": not current_status, "updated_at": datetime.now().isoformat()}
        ).eq("id", str(reminder_id)).eq("user_id", current_user["id"]).execute()
        
        # Update Redis cache
        redis_key = f"reminder:{current_user['id']}:{reminder_id}"
        redis.setex(
            redis_key,
            60 * 60 * 24,  # 24 hour expiry
            json.dumps(result.data[0])
        )
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))