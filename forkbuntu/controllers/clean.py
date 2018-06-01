from cement.core.controller import expose
from cfoundation import Controller
from os import path
import json

class Clean(Controller):
    class Meta:
        description = 'clean temporary files and cache'
        label = 'clean'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--source', '--src', '-s'], {
                'action': 'store',
                'dest': 'src',
                'help': 'source path',
                'required': False
            }),
            (['output'], {
                'action': 'store',
                'help': 'built iso output path',
                'nargs': '*'
            })
        ]

    @expose()
    def default(self):
        steps = self.app.steps
        pargs = self.app.pargs
        if pargs.output and len(pargs.output) > 0:
            self.app.conf.paths.output = path.abspath(pargs.output[0])
        steps.clean.start(True)
