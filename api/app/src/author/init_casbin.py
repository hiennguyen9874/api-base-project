import casbin

from app.core.settings import settings
from app.src.author.services import casbin_service

__all__ = ["init_casbin"]


async def init_casbin(casbin_enforcer: casbin.Enforcer) -> None:
    file_enforcer = casbin.AsyncEnforcer(settings.CASBIN.PATH_MODEL, settings.CASBIN.PATH_POLICY)
    await file_enforcer.load_policy()

    for policy in await casbin_service.get_policy_list(enforcer=file_enforcer):
        if not await casbin_service.has_policy(enforcer=casbin_enforcer, p=policy):
            await casbin_service.create_policy(enforcer=casbin_enforcer, p=policy)

    for group in await casbin_service.get_group_list(enforcer=file_enforcer):
        if not await casbin_service.has_grouping(enforcer=casbin_enforcer, g=group):
            await casbin_service.create_group(enforcer=casbin_enforcer, g=group)

    await casbin_enforcer.save_policy()
