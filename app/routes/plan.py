from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import RunRequest, PlanResponse, PlanItem
from app.deps import get_current_user
from app.services.optimizer import run_qubo_plan
from typing import List

router = APIRouter()

@router.post('/run', response_model=PlanResponse)
def run_plan(req: RunRequest, username: str = Depends(get_current_user)):
    # username available for audit/logging
    try:
        energy, plan = run_qubo_plan(req.features.dict(), days=req.days, user_id=req.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    items = [PlanItem(**p) for p in plan]
    return PlanResponse(energy=energy, plan=items, meta={'requested_by': username})
