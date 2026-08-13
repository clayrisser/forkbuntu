from __future__ import annotations

import json

from munch import Munch

from ..step import Step


class Initialize(Step):
    cache = False
    messages = Munch(past="initialized", present="initializing")

    def run(self, *args: object) -> None:
        c = self.app.conf
        s = self.app.services
        s.setup.init()
        if c.keyring:
            s.gpg.setup()
            self.app.gpg_keys = s.gpg.get_keys()

    def finish(self, cached: bool) -> bool:
        result = super().finish(cached)
        c = self.app.conf
        log = self.app.log
        if c.keyring:
            log.debug(
                "gpg_keys: " + json.dumps(self.app.gpg_keys, indent=4, sort_keys=True)
            )
        return result
