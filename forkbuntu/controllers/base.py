from cement.core.controller import expose
from cfoundation import Controller
from halo import Halo
from munch import munchify
from pydash import _
import logging
import json

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Fork the Ubuntu OS'

    @expose()
    def default(self):
        log = self.app.log
        c = self.app.conf
        self.app.spinner = Halo(text='initializing').start()
        self.app.services.setup.init()
        self.app.spinner.succeed('initialized')
        self.app.spinner = Halo(text='unpacking iso').start()
        self.app.services.unpack.iso()
        self.app.spinner.succeed('unpacked iso')
        self.app.spinner = Halo(text='unpacking filesystem').start()
        self.app.services.unpack.filesystem()
        self.app.spinner.succeed('unpacked filesystem')
        self.app.spinner = Halo(text='loading config').start()
        setattr(self.app, 'release', self.app.services.configure.load_release())
        release = self.app.release
        log.debug('release: ' + json.dumps(release, indent=4, sort_keys=True))
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'codename': c.codename if 'codename' in c else release.distrib_codename,
            'distrib_id': c.distrib_id if 'distrib_id' in c else release.distrib_id,
            'name': c.name if 'name' in c else release.distrib_name,
            'version': c.version if 'version' in c else release.distrib_version
        }))
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'description': c.description if 'description' in c else c.name + ' ' + c.version,
            'hostname': c.hostname if 'hostname' in c else _.snake_case(c.name)
        }))
        log.debug('conf: ' + json.dumps(self.app.conf, indent=4, sort_keys=True))
        self.app.spinner.succeed('loaded config')
        self.app.spinner = Halo(text='merging iso').start()
        self.app.services.configure.merge_iso()
        self.app.spinner.succeed('merged iso')
        self.app.spinner = Halo(text='merging filesystem').start()
        self.app.services.configure.merge_filesystem()
        self.app.spinner.succeed('merged filesystem')
        self.app.spinner = Halo(text='configuring filesystem').start()
        self.app.services.configure.filesystem()
        self.app.spinner.succeed('configured filesystem')
        self.app.spinner = Halo(text='signing iso').start()
        self.app.services.configure.sign_iso()
        self.app.spinner.succeed('signed iso')
        self.app.spinner = Halo(text='packing filesystem').start()
        self.app.services.pack.filesystem()
        self.app.spinner.succeed('packed filesystem')
        self.app.spinner = Halo(text='packing iso').start()
        self.app.services.pack.iso()
        self.app.spinner.succeed('packed iso')
        self.app.spinner = Halo(text='cleaning').start()
        self.app.services.clean.tmp()
        self.app.spinner.succeed('cleaned')
        self.app.spinner = Halo(text='iso created: ' + c.paths.output).succeed()
