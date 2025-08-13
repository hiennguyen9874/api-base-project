# Import all the models, so that Base has them before being
# imported by Alembic
from app.src.author.db_models import CasbinRule  # noqa
from app.src.db_base import Base  # noqa
from app.src.items.db_models import Item  # noqa
from app.src.users.db_models import User  # noqa
