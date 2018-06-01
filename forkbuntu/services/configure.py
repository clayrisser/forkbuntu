from cfoundation import Service
from munch import Munch
from os import path
import re

class Configure(Service):
    def load_release(self):
        c = self.app.conf
        release = Munch()
        matches = None
        with open(path.join(c.paths.filesystem, 'etc/lsb-release'), 'r') as f:
            matches = re.finditer(r'(^[^=\n\s]+)\=([^\=\n]*$)', f.read(), re.MULTILINE)
        for key, match in enumerate(matches):
            groups = match.groups()
            if (len(groups) >= 2):
                value = groups[1]
                if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                    value = value[1:-1]
                release[groups[0].lower()] = value
        return release
