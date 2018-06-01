from cement.core.controller import expose
from cfoundation import Controller
from halo import Halo
from munch import munchify
from os import path
from pydash import _
import json

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Fork the Ubuntu OS'
        arguments = [
            (['--reset', '-r'], {
                'action': 'store_true',
                'dest': 'reset',
                'help': 'reset cache',
                'required': False
            }),
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
        pargs = self.app.pargs
        s = self.app.services
        spinner = self.app.spinner
        steps = self.app.steps
        if pargs.debug:
            self.app.conf.debug = True
        if pargs.output and len(pargs.output) > 0:
            self.app.conf.paths.output = path.abspath(pargs.output[0])
        c = self.app.conf
        setattr(self.app, 'finished', s.cache.is_finished())
        if pargs.reset:
            steps.clean.start(pargs.reset)
        s.cache.started()
        steps.pack_iso.start()
        steps.clean.start()
        spinner.start('iso created: ' + c.paths.output).succeed()
        s.cache.finished()
