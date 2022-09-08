from fastapi import APIRouter

router = APIRouter()

from api.starter import router as starter

router.include_router(starter)
