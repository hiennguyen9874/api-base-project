import casbin

from app.core.settings import settings

from .casbin_adapter import SqlAlchemyAdapter


async def init_casbin_enforcer() -> casbin.Enforcer:
    adapter = SqlAlchemyAdapter()
    casbin_enforcer = casbin.AsyncEnforcer(settings.CASBIN.PATH_MODEL, adapter, enable_log=False)
    casbin_enforcer.enable_auto_save(True)
    await casbin_enforcer.load_policy()

    return casbin_enforcer
