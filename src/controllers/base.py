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
        config = self.app.services.config.load()
        print(json.dumps(config, indent=4, sort_keys=True))
        paths = config['paths']
        self.app.services.unpack.mount_iso(paths['iso'], paths['mount'])
        self.app.services.configure.merge_files(
            paths['working'],
            paths['mount'],
            config['packages']
        )
        self.app.services.pack.sign(paths['mount'])
        self.app.services.pack.build(paths['mount'], paths['output'])
