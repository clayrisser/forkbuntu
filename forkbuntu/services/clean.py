from __future__ import annotations

import os
import shutil
from os import path

from ..service import Service


class Clean(Service):
    def tmp(self) -> None:
        c = self.app.conf
        if path.exists(c.paths.tmp):
            shutil.rmtree(c.paths.tmp)

    def cache(self) -> None:
        c = self.app.conf
        if path.exists(c.paths.cwt):
            shutil.rmtree(c.paths.cwt)
        if path.exists(c.paths.output):
            os.remove(c.paths.output)
