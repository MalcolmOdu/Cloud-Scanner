##The endpoint that confirms the web server is alive and responding.

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}
