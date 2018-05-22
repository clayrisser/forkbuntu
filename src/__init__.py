from . import controllers, services
from cfoundation import create_app

App = create_app(
    controllers=controllers,
    services=services
)
