"""Route package for backend HTTP endpoints."""

from flask import Blueprint

api = Blueprint("api", __name__)

# Import route modules so their decorators register on the shared blueprint.
from . import demo_resources  # noqa: F401,E402
from . import health  # noqa: F401,E402
from . import products  # noqa: F401,E402
from . import stores  # noqa: F401,E402
from . import tags  # noqa: F401,E402
