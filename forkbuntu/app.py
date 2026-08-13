from __future__ import annotations

import logging
import logging.config
from argparse import Namespace
from os import path

import yaml
from halo import Halo
from munch import Munch

from .config import load_conf
from .services import create_services
from .steps import create_steps


class App:
    def __init__(self, pargs: Namespace) -> None:
        self.pargs = pargs
        output = pargs.output[0] if pargs.output else None
        self.conf = load_conf(pargs.src, output=output, debug=pargs.debug)
        self.log = self._create_log()
        self.spinner = Halo(spinner="dots")
        self.finished = False
        self.gpg_keys: list[Munch] = []
        self.release = Munch()
        self.steps_ran = Munch()
        self.services = create_services(self)
        self.steps = create_steps(self)

    def build(self) -> int:
        c = self.conf
        s = self.services
        spinner = self.spinner
        steps = self.steps
        self.finished = s.cache.is_finished()
        if self.pargs.reset:
            steps.clean.start(True)
        s.cache.started()
        steps.pack_iso.start()
        steps.clean.start()
        spinner.start("iso created: " + c.paths.output).succeed()
        s.cache.finished()
        return 0

    def clean(self) -> int:
        self.steps.clean.start(True)
        return 0

    def _create_log(self) -> logging.Logger:
        logger_path = path.join(path.dirname(path.realpath(__file__)), "logger.yml")
        with open(logger_path) as f:
            logging.config.dictConfig(yaml.safe_load(f))
        log = logging.getLogger("forkbuntu")
        if self.conf.debug:
            log.setLevel(logging.DEBUG)
        return log
