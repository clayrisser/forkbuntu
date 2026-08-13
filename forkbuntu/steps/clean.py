from __future__ import annotations

from munch import Munch

from ..step import Step


class Clean(Step):
    messages = Munch(past="cleaned", present="cleaning")
    cache = False
    requires = ["initialize"]

    def run(self, *args: object) -> None:
        reset = bool(args[0]) if args else False
        s = self.app.services
        s.clean.tmp()
        if reset:
            s.clean.cache()
