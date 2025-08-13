import json
from typing import Sequence

from redis.asyncio import Redis

from app.core.settings import settings
from app.src.cache_repository import BaseCacheRepository

from .db_models import CasbinRule
from .schemas import CasbinRuleInDB


class CasbinRuleCacheRepository(BaseCacheRepository):
    ## Common
    @staticmethod
    def _generate_redis_casbin_rule() -> str:  # pylint: disable=redefined-builtin
        return "Cache:CasbinRule:all"

    async def create_cache_all(
        self, connection: Redis, obj_casbin_rules: Sequence[CasbinRule]
    ) -> None:
        casbin_rules_in_db = [
            CasbinRuleInDB.model_validate(obj_casbin_rule) for obj_casbin_rule in obj_casbin_rules
        ]

        await self.create(
            connection=connection,
            key=self._generate_redis_casbin_rule(),
            value=json.dumps(
                [
                    casbin_rule_in_db.model_dump(mode="json")
                    for casbin_rule_in_db in casbin_rules_in_db
                ]
            ),
            ttl=settings.REDIS_CACHE.CASBIN_TTL,
        )

    async def get_cache_all(self, connection: Redis) -> list[CasbinRule] | None:
        db_objs = await self.get(
            connection=connection,
            key=self._generate_redis_casbin_rule(),
            ttl=settings.REDIS_CACHE.CASBIN_TTL,
        )
        if not db_objs:
            return None

        db_objs = json.loads(db_objs.decode())

        casbin_rules_in_db = [CasbinRuleInDB.model_validate(db_obj) for db_obj in db_objs]

        return [
            CasbinRule(**casbin_rule_in_db.model_dump()) for casbin_rule_in_db in casbin_rules_in_db
        ]

    async def delete_cache_all(self, connection: Redis) -> None:
        await self.delete(connection=connection, key=self._generate_redis_casbin_rule())


casbin_rule_cache_repository = CasbinRuleCacheRepository(repository_name="casbin_rule")
