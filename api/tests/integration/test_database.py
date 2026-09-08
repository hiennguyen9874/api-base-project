import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
async def test_database_session(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT 1"))

    assert result.scalar_one() == 1
