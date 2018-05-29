from cement.core.controller import expose
from cfoundation import Controller
from halo import Halo
from munch import munchify
from pydash import _
import json

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Fork the Ubuntu OS'

    @expose()
    def default(self):
        steps = self.app.steps
        steps.clean.start()
        spinner.start('iso created: ' + c.paths.output).succeed()
