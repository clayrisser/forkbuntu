from cement.core.foundation import CementApp
from pydash import _
import inspect
import re

def create_app(controllers, services):
    class App(CementApp):
        class Meta:
            label = 'forkbuntu'
            base_controller = controllers.Base
            handlers = [
                controllers.Clean
            ]

        def __init__(self):
            super().__init__()
            self.services = self.__load_services(services)

        def run(self):
            super().run()

        def __load_services(self, services):
            context = Object()
            for key in dir(services):
                matches = re.findall(r'[A-Z].*', key)
                if len(matches) > 0:
                    setattr(context, _.snake_case(key), getattr(services, key)(self))
            return context

    return App

class Object():
    pass
