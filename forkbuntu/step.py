from __future__ import annotations

from os import path
from typing import TYPE_CHECKING

from munch import Munch

if TYPE_CHECKING:
    from .app import App


class Step:
    cache = True
    agnostic = False
    root = False
    messages: Munch
    requires: list[str] = []
    checksum_paths: list[str] | None = None
    has_paths: list[str] | None = None

    def __init__(self, name: str, app: App) -> None:
        self.name = name
        self.app = app
        self.log = app.log

    def init(self) -> None:
        pass

    def run(self, *args: object) -> None:
        raise NotImplementedError

    def run_required(self) -> bool:
        steps = self.app.steps
        steps_ran = self.app.steps_ran
        cached = True
        if len(self.requires) <= 0:
            return False
        for required in self.requires:
            if required in steps_ran:
                maybe_cached = steps_ran[required]
            else:
                maybe_cached = getattr(steps, required).start()
            if not maybe_cached:
                cached = maybe_cached
        return cached

    def is_cached(self, cached: bool) -> bool:
        s = self.app.services
        if self.root and not self.app.finished:
            return False
        if self.checksum_paths is None and self.has_paths is None:
            return cached
        if not cached and not self.root and not self.agnostic:
            return cached
        cached = True
        for checksum_path in self.checksum_paths or []:
            checksum = s.cache.checksum(checksum_path)
            cached_checksums = s.cache.get_checksums(self.name)
            if checksum not in cached_checksums:
                cached = False
                break
        for has_path in self.has_paths or []:
            if not path.exists(has_path):
                cached = False
                break
        return cached

    def register(self) -> None:
        s = self.app.services
        if self.checksum_paths is not None:
            s.cache.register(self.name)

    def start(self, *args: object) -> bool:
        self.init()
        spinner = self.app.spinner
        cached = self.run_required()
        original_cached = cached
        spinner.start(self.messages.present)
        cached = self.is_cached(cached)
        if cached:
            if self.agnostic:
                cached = original_cached
            if self.cache:
                return self.cached(cached)
        self.run(*args)
        self.register()
        return self.finish(cached)

    def cached(self, cached: bool) -> bool:
        spinner = self.app.spinner
        self.app.steps_ran[self.name] = cached
        spinner.warn(self.messages.past + " using cache")
        return cached

    def finish(self, cached: bool) -> bool:
        spinner = self.app.spinner
        self.app.steps_ran[self.name] = cached
        spinner.succeed(self.messages.past)
        return cached
