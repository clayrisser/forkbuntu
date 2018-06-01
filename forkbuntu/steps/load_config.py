from ..step import Step
from time import sleep
from munch import munchify
from os import path
import json
from pydash import _

class LoadConfig(Step):
    messages = munchify({
        'past': 'loaded config',
        'present': 'loading config'
    })
    cache = False
    requires = [
        'unpack_filesystem'
    ]

    def __init__(self, name, app):
        super().__init__(name, app)
        c = app.conf

    def run(self):
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        spinner = self.app.spinner
        setattr(self.app, 'release', s.configure.load_release())
        release = self.app.release
        spinner.stop()
        log.debug('release: ' + json.dumps(release, indent=4, sort_keys=True))
        spinner.start()
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'codename': c.codename if 'codename' in c else release.distrib_codename,
            'distrib_id': c.distrib_id if 'distrib_id' in c else release.distrib_id,
            'name': c.name if 'name' in c else release.distrib_name,
            'version': c.version if 'version' in c else release.distrib_version
        }))
        preseed = c.preseed if ('preseed' in c and c.preseed != True) else _.snake_case(c.name)
        if _.is_string(preseed) and preseed[len(preseed) - 5:] != '.seed':
            preseed = preseed + '.seed'
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'description': c.description if 'description' in c else c.name + ' ' + c.version,
            'hostname': c.hostname if 'hostname' in c else _.snake_case(c.name),
            'preseed': preseed
        }))

    def finish(self, status):
        result = super().finish(status)
        log = self.app.log
        log.debug('conf: ' + json.dumps(self.app.conf, indent=4, sort_keys=True))
        return result
