from fastapi import APIRouter

router = APIRouter()

from api.starter import router as starter
from api.pretest import router as pretest

router.include_router(starter, tags=["starter"])
router.include_router(pretest, tags=["pretest"])
