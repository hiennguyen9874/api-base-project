from app.core.http.api_router import APIRouter

from .v0.test_common import router as test_common_router
from .v0.test_task import router as test_task_router

router = APIRouter()
router.include_router(test_task_router, prefix="/v0/test-task", tags=["Test Task"])
router.include_router(test_common_router, prefix="/v0/test-common", tags=["Test Common"])
