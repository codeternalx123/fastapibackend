from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ReportRequest
from app.deps import get_current_user
from app.utils.report import save_report_html

router = APIRouter()

@router.post('/')
def create_report(req: ReportRequest, username: str = Depends(get_current_user)):
    try:
        path = save_report_html(req.plan, req.meta)
        # In production return a presigned S3 URL or similar
        url = f"/reports/{path.split('/')[-1]}"
        return {'report_url': url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
