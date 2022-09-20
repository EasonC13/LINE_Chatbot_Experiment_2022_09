from fastapi import APIRouter

router = APIRouter()

from api.starter import router as starter
from api.pretest import router as pretest
from api.posttest import router as posttest

router.include_router(starter, tags=["starter"], prefix="/starter")
router.include_router(pretest, tags=["pretest"], prefix="/pretest")
router.include_router(posttest, tags=["posttest"], prefix="/posttest")
