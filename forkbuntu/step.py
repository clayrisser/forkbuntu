from munch import Munch
from os import path
from pydash import _

steps_ran = Munch()

class Step():
    cache = True

    def __init__(self, name, app):
        self.name = name
        self.app = app
        self.log = app.log

    def run_required(self):
        global steps_ran
        steps = self.app.steps
        cached = True
        if not hasattr(self, 'requires'):
            return False
        if len(self.requires) <= 0:
            cached = False
        for required in self.requires:
            maybe_cached = True
            if _.includes(_.keys(steps_ran), required):
                maybe_cached = steps_ran[required]
            else:
                maybe_cached = getattr(steps, required).start()
            if not maybe_cached:
                cached = maybe_cached
        return cached

    def is_cached(self, cached):
        s = self.app.services
        spinner = self.app.spinner
        if hasattr(self, 'root') and self.root and not self.app.finished:
            return False
        if not hasattr(self, 'checksum_paths') and not hasattr(self, 'has_paths'):
            return cached
        if not cached and (not hasattr(self, 'root') or not self.root) and \
           (not hasattr(self, 'agnostic') or not self.agnostic):
            return cached
        cached = True
        checksum_paths = self.checksum_paths if hasattr(self, 'checksum_paths') else []
        has_paths = self.has_paths if hasattr(self, 'has_paths') else []
        for checksum_path in checksum_paths:
            checksum = s.cache.checksum(checksum_path)
            cached_checksums = s.cache.get_checksums(self.name)
            if not _.includes(cached_checksums, checksum):
                cached = False
                break
        for has_path in has_paths:
            if not path.exists(has_path):
                cached = False
                break
        return cached

    def register(self):
        s = self.app.services
        if hasattr(self, 'checksum_paths'):
            s.cache.register(self.name)

    def start(self):
        spinner = self.app.spinner
        cached = self.run_required()
        origional_cached = cached
        spinner.start(self.messages.present)
        cached = self.is_cached(cached)
        if cached:
            if hasattr(self, 'agnostic') and self.agnostic:
                cached = origional_cached
            if not hasattr(self, 'cache') or self.cache != False:
                return self.cached(cached)
        self.run()
        self.register()
        return self.finish(cached)

    def cached(self, cached):
        global steps_ran
        s = self.app.services
        spinner = self.app.spinner
        steps_ran[self.name] = cached
        spinner.warn(self.messages.past + ' using cache')
        return cached

    def finish(self, cached):
        s = self.app.services
        spinner = self.app.spinner
        steps_ran[self.name] = cached
        spinner.succeed(self.messages.past)
        return cached
