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
        self.app.services.unpack.mount_iso()
        self.app.services.configure.merge_files()
        self.app.services.pack.sign()
        self.app.services.pack.build()
