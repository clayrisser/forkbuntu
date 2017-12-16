from cement.core.controller import expose
from cfoundation import Controller

class BaseController(Controller):
    class Meta:
        label = 'base'
        description = 'Create Ubuntu fork'

    @expose(hide=True)
    def default(self):
        return
