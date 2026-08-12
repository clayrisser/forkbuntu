from __future__ import annotations

import json
from os import path

from munch import Munch

from ..helpers import snake_case
from ..step import Step


class LoadConfig(Step):
    messages = Munch(past="loaded config", present="loading config")
    cache = False
    requires = ["unpack_filesystem"]

    def run(self, *args: object) -> None:
        c = self.app.conf
        log = self.app.log
        s = self.app.services
        spinner = self.app.spinner
        self.app.release = s.configure.load_release()
        release = self.app.release
        spinner.stop()
        log.debug("release: " + json.dumps(release, indent=4, sort_keys=True))
        spinner.start()
        c.codename = c.codename if "codename" in c else release.distrib_codename
        c.origin = c.origin if "origin" in c else release.distrib_id
        c.name = c.name if "name" in c else release.distrib_id
        c.version = str(c.version if "version" in c else release.distrib_release)
        c.description = (
            c.description if "description" in c else c.name + " " + c.version
        )
        c.hostname = (
            c.hostname if "hostname" in c else snake_case(c.name).replace("_", "-")
        )
        c.preseed = self._resolve_preseed()

    def finish(self, cached: bool) -> bool:
        result = super().finish(cached)
        log = self.app.log
        log.debug("conf: " + json.dumps(self.app.conf, indent=4, sort_keys=True))
        return result

    def _resolve_preseed(self) -> str | bool:
        """Preseeding targets the legacy debian-installer; default it on for
        d-i isos only. Modern casper/subiquity isos use ``autoinstall``.
        """
        c = self.app.conf
        preseed: str | bool = False
        if "preseed" in c:
            preseed = c.preseed
        elif path.basename(c.paths.install) == "install":
            preseed = True
        if preseed is True:
            preseed = snake_case(c.name)
        if isinstance(preseed, str) and not preseed.endswith(".seed"):
            preseed = preseed + ".seed"
        return preseed
