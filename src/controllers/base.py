from cement.core.controller import expose
from cfoundation import Controller
import json

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Fork the Ubuntu OS'

    @expose()
    def default(self):
        self.app.services.setup.init()
        print(json.dumps(self.app.conf, indent=4, sort_keys=True))
        self.app.services.unpack.iso()
        self.app.services.configure.merge_iso()
        self.app.services.unpack.filesystem()
        self.app.services.configure.merge_filesystem()
        self.app.services.configure.chroot()
        self.app.services.configure.sign()
        self.app.services.pack.filesystem()
        self.app.services.pack.iso()
        self.app.services.clean.tmp()
