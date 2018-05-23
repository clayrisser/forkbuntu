from cement.core.controller import expose
from cfoundation import Controller
from munch import munchify
from pydash import _
import json

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Fork the Ubuntu OS'

    @expose()
    def default(self):
        c = self.app.conf
        self.app.services.setup.init()
        self.app.services.unpack.iso()
        self.app.services.unpack.filesystem()
        setattr(self.app, 'release', self.app.services.configure.load_release())
        release = self.app.release
        print('release', json.dumps(release, indent=4, sort_keys=True))
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'codename': c.codename if 'codename' in c else release.distrib_codename,
            'distrib_id': c.distrib_id if 'distrib_id' in c else release.distrib_id,
            'name': c.name if 'name' in c else release.distrib_name,
            'version': c.version if 'version' in c else release.distrib_version
        }))
        self.app.conf = munchify(_.merge({}, self.app.conf, {
            'description': c.description if 'description' in c else c.name + ' ' + c.version
        }))
        print('conf', json.dumps(self.app.conf, indent=4, sort_keys=True))
        self.app.services.configure.merge_iso()
        self.app.services.configure.merge_filesystem()
        self.app.services.configure.chroot()
        self.app.services.configure.sign()
        self.app.services.pack.filesystem()
        self.app.services.pack.iso()
        self.app.services.clean.tmp()
