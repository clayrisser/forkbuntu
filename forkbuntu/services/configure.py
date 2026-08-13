from __future__ import annotations

import re
from os import path

from munch import Munch

from ..service import Service


class Configure(Service):
    def load_release(self) -> Munch:
        c = self.app.conf
        release = Munch()
        with open(path.join(c.paths.filesystem, "etc/lsb-release")) as f:
            matches = re.finditer(r"(^[^=\n\s]+)\=([^\=\n]*$)", f.read(), re.MULTILINE)
        for match in matches:
            groups = match.groups()
            if len(groups) >= 2:
                value = groups[1]
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                release[groups[0].lower()] = value
        return release
