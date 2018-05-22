from cement.core.controller import expose
from cfoundation import Controller

class Clean(Controller):
    class Meta:
        label = 'clean'
        description = 'Clean'
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose()
    def default(self):
        print('cleaning . . .')
