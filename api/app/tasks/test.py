from loguru import logger

from app.core.messaging.taskiq_broker import broker

__all__ = ["test_task", "task_schedule_work"]


@broker.task(task_name="test_task_2")
async def test_task_2(word: str) -> str:
    logger.info("test_task_2: {}", word)
    return f"test task return {word}"


@broker.task(task_name="test_task")
async def test_task(word: str) -> str:
    logger.info("test_task: {}", word)
    return f"test task return {word}"


@broker.task(
    task_name="task_schedule_work",
    # schedule=[{"cron": "*/1 * * * *", "args": []}],
)
async def task_schedule_work() -> None:
    logger.info("task_schedule_work run")
