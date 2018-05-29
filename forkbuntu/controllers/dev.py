from cement.core.controller import expose
from cfoundation import Controller
import json

class Dev(Controller):
    class Meta:
        description = 'Development'
        label = 'dev'
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose()
    def default(self):
        log = self.app.log
        c = self.app.conf
        s = self.app.services
