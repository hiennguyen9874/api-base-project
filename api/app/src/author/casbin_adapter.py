from casbin import persist
from casbin.model.model import Model
from casbin.persist.adapters.asyncio import AsyncAdapter

from app.core.cache.cache_connections import async_cache_connection
from app.core.db.db_connections import async_db_connection

from . import schemas
from .services import casbin_rule_service

__all__ = ["SqlAlchemyAdapter", "SqlAlchemyFilter"]


class SqlAlchemyFilter:
    ptype: list[str] = []
    v0: list[str] = []
    v1: list[str] = []
    v2: list[str] = []
    v3: list[str] = []
    v4: list[str] = []
    v5: list[str] = []


class SqlAlchemyAdapter(AsyncAdapter):
    """the interface for Casbin adapters."""

    def __init__(self, filtered: bool = False) -> None:
        self._filtered = filtered

    def is_filtered(self) -> bool:
        """IsFiltered returns true if the loaded policy has been filtered
        Marks if the loaded policy is filtered or not
        """
        return self._filtered

    async def load_policy(self, model: Model) -> None:
        """loads all policy rules from the storage."""
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                casbin_rules = await casbin_rule_service.get_all(
                    db=db, cache_connection=cache_connection
                )

        if casbin_rules is None:
            return

        for casbin_rule in casbin_rules:
            persist.load_policy_line(str(casbin_rule), model)

    async def load_filtered_policy(self, model: Model, filter: SqlAlchemyFilter) -> None:
        """loads all policy rules from the storage"""
        async with async_db_connection.session() as db:
            casbin_rules = await casbin_rule_service.get_all_by_list_attribute(
                db=db,
                ptype=filter.ptype,
                v0=filter.v0,
                v1=filter.v1,
                v2=filter.v2,
                v3=filter.v3,
                v4=filter.v4,
                v5=filter.v5,
            )

            for casbin_rule in casbin_rules:
                persist.load_policy_line(str(casbin_rule), model)
            self._filtered = True

    async def save_policy(self, model: Model) -> bool:
        """saves all policy rules to the storage."""
        objs_in = []
        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    objs_in.append(
                        schemas.CasbinRuleCreate(
                            ptype=ptype,
                            **{f"v{id}": value for id, value in enumerate(rule)},
                        )
                    )

        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                await casbin_rule_service.save(
                    db=db,
                    cache_connection=cache_connection,
                    objs_in=objs_in,
                )

        return True

    async def add_policy(self, sec: str, ptype: str, rule: list[str]) -> None:
        """adds a policy rule to the storage."""
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                await casbin_rule_service.create(
                    db=db,
                    cache_connection=cache_connection,
                    obj_in=schemas.CasbinRuleCreate(
                        ptype=ptype,
                        **{f"v{id}": value for id, value in enumerate(rule)},
                    ),
                )

    async def add_policies(self, sec: str, ptype: str, rules: list[list[str]]) -> None:
        """AddPolicies adds policy rules to the storage."""
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                await casbin_rule_service.creates(
                    db=db,
                    cache_connection=cache_connection,
                    objs_in=[
                        schemas.CasbinRuleCreate(
                            ptype=ptype,
                            **{f"v{id}": value for id, value in enumerate(rule)},
                        )
                        for rule in rules
                    ],
                )

    async def remove_policy(self, sec: str, ptype: str, rule: list[str]) -> bool:
        """removes a policy rule from the storage."""
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                return await casbin_rule_service.delete_by_attribute(
                    db=db,
                    cache_connection=cache_connection,
                    ptype=ptype,
                    **{f"v{id}": value for id, value in enumerate(rule)},
                )

    async def remove_policies(self, sec: str, ptype: str, rules: list[list[str]]) -> None:
        """RemovePolicies removes policy rules from the storage."""
        if not rules:
            return

        for rule in rules:
            await self.remove_policy(sec, ptype, rule)

    async def remove_filtered_policy(  # type: ignore
        self, sec: str, ptype: str, field_index: int, *field_values
    ) -> bool:
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        if not (0 <= field_index <= 5):
            return False

        if not (1 <= field_index + len(field_values) <= 6):
            return False

        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                return await casbin_rule_service.delete_by_attribute(
                    db=db,
                    cache_connection=cache_connection,
                    ptype=ptype,
                    **{
                        f"v{field_index + id}": value
                        for id, value in enumerate(field_values)
                        if value != ""
                    },
                )

    async def update_policy(
        self, sec: str, ptype: str, old_rule: list[str], new_rule: list[str]
    ) -> None:
        """
        update_policy updates a policy rule from storage.
        This is part of the Auto-Save feature.
        """
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                casbin_rule = await casbin_rule_service.get_by_attribute(
                    db=db,
                    ptype=ptype,
                    **{f"v{id}": value for id, value in enumerate(old_rule)},
                )

                if casbin_rule is None:
                    return

                casbin_rule = await casbin_rule_service.update(
                    db=db,
                    cache_connection=cache_connection,
                    db_obj=casbin_rule,
                    obj_in=schemas.CasbinRuleUpdate(
                        v0=new_rule[0] if len(new_rule) >= 1 else None,
                        v1=new_rule[1] if len(new_rule) >= 2 else None,
                        v2=new_rule[2] if len(new_rule) >= 3 else None,
                        v3=new_rule[3] if len(new_rule) >= 4 else None,
                        v4=new_rule[4] if len(new_rule) >= 5 else None,
                        v5=new_rule[5] if len(new_rule) >= 6 else None,
                    ),
                )

    async def update_policies(
        self,
        sec: str,
        ptype: str,
        old_rules: list[list[str]],
        new_rules: list[list[str]],
    ) -> None:
        """
        UpdatePolicies updates some policy rules to storage, like db, redis.
        """
        for old_rule, new_rule in zip(old_rules, new_rules, strict=True):
            await self.update_policy(sec, ptype, old_rule, new_rule)

    async def update_filtered_policies(  # type: ignore
        self, sec, ptype, new_rules: list[list[str]], field_index, *field_values
    ) -> None:
        """
        update_filtered_policies deletes old rules and adds new rules.
        """
        async with async_db_connection.session() as db:
            async with async_cache_connection.session() as cache_connection:
                await casbin_rule_service.update_by_attribute(
                    db=db,
                    cache_connection=cache_connection,
                    objs_in=[
                        schemas.CasbinRuleCreate(
                            ptype=ptype,
                            **{f"v{id}": value for id, value in enumerate(rule)},
                        )
                        for rule in new_rules
                    ],
                    ptype=ptype,
                    **{
                        f"v{i}": field_values[i - field_index]
                        for i in range(len(field_values))
                        if field_index <= i and i < field_index + len(field_values)
                    },
                )
