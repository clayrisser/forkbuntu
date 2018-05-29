from cement.core.controller import expose
from cfoundation import Controller
import json

class Clean(Controller):
    class Meta:
        description = 'Clean'
        label = 'clean'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--cache'], {
                'action': 'store_true',
                'dest': 'cache',
                'help': 'Clean cache',
                'required': False
            })
        ]

    @expose()
    def default(self):
        steps = self.app.steps
        steps.clean.start()
