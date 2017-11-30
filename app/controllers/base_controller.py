from cement.core.controller import CementBaseController, expose

class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Create Ubuntu fork'

    @expose(hide=True)
    def default(self):
        return
