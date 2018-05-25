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
        s = self.app.services
        spinner = self.app.spinner
        spinner.start('initializing')
        s.setup.init()
        spinner.succeed('initialized')
        setattr(self.app, 'gpg_keys', s.gpg.get_keys())
        gpg_keys = self.app.gpg_keys
        log.debug('gpg_keys: ' + json.dumps(gpg_keys, indent=4, sort_keys=True))
        spinner.start('unpacking iso')
        s.unpack.iso()
        spinner.succeed('unpacked iso')
        spinner.start('unpacking filesystem')
        s.unpack.filesystem()
        spinner.succeed('unpacked filesystem')
        spinner.start('loading config')
        setattr(self.app, 'release', s.configure.load_release())
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
        spinner.succeed('loaded config')
        spinner.start('merging iso')
        s.configure.merge_iso()
        spinner.succeed('merged iso')
        spinner.start('merging filesystem')
        s.configure.merge_filesystem()
        spinner.succeed('merged filesystem')
        spinner.start('building keyring')
        s.gpg.build_keyring()
        spinner.succeed('built keyring')
        spinner.start('creating extras')
        s.extras.create()
        spinner.succeed('created extras')
        spinner.start('configuring filesystem')
        s.configure.filesystem()
        spinner.succeed('configured filesystem')
        spinner.start('signing iso')
        s.configure.sign_iso()
        spinner.succeed('signed iso')
        spinner.start('packing filesystem')
        s.pack.filesystem()
        spinner.succeed('packed filesystem')
        spinner.start('packing iso')
        s.pack.iso()
        spinner.succeed('packed iso')
        spinner.start('cleaning')
        s.clean.tmp()
        spinner.succeed('cleaned')
        spinner.start('iso created: ' + c.paths.output).succeed()
