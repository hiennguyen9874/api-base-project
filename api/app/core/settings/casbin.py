from pydantic import BaseModel


class CasbinSettings(BaseModel):
    PATH_MODEL: str = "/app/app/configs/author/casbin_model.conf"
    PATH_POLICY: str = "/app/app/configs/author/rbac_policy.csv"

    DEFAULT_ROLE: str = "role:data_admin"
