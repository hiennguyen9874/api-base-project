from typing import Annotated, Any

from fastapi import Depends

from app.core.http.api_router import APIRouter
from app.schemas import (
    create_successful_response,
    Msg,
    SuccessfulResponse,
)
from app.src.authen.dependencies import get_current_active_authorized
from app.src.users.db_models import User
from app.tasks import test_task as test_task_task

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_active_authorized)]


@router.post("/test-task", response_model=SuccessfulResponse[Msg], status_code=201)
async def test_task(
    *,
    msg: Msg,
    current_user: CurrentUser,
) -> Any:
    """
    Test Task.
    """
    task = await test_task_task.kiq(msg.msg)
    result = await task.wait_result()
    return create_successful_response(data={"msg": result.return_value})
