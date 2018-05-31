from pydash import _
from munch import Munch

steps_run = Munch()

class Step():
    global steps_run
    cache = True

    def __init__(self, name, app):
        self.name = name
        self.app = app
        self.log = app.log

    def run_required(self):
        steps = self.app.steps
        cached = True
        if not hasattr(self, 'requires'):
            return False
        if len(self.requires) <= 0:
            cached = False
        for required in self.requires:
            maybe_cached = True
            if _.includes(_.keys(steps_run), required):
                maybe_cached = steps_run[required]
            else:
                maybe_cached = getattr(steps, required).start()
            if not maybe_cached:
                cached = maybe_cached
        return cached

    def checksum(self):
        s = self.app.services
        if not hasattr(self, 'checksum_paths'):
            return True
        for checksum_path in self.checksum_paths:
            checksum = s.cache.checksum(checksum_path)
            cached_checksums = s.cache.get(self.name)
            if not _.includes(cached_checksums, checksum):
                return False
        return True

    def register(self):
        s = self.app.services
        if hasattr(self, 'checksum_paths'):
            s.cache.register(self.name)

    def start(self):
        spinner = self.app.spinner
        cached = self.run_required()
        origional_cached = cached
        spinner.start(self.messages.present)
        if hasattr(self, 'checksum_paths'):
            cached = self.checksum()
        if cached:
            if hasattr(self, 'agnostic') and self.agnostic:
                cached = origional_cached
            if not hasattr(self, 'cache') or self.cache != False:
                return self.cached(cached)
        self.run()
        self.register()
        return self.finish(cached)

    def cached(self, cached):
        global steps_run
        spinner = self.app.spinner
        steps_run[self.name] = cached
        spinner.warn(self.messages.cache)
        return cached

    def finish(self, cached):
        global steps_run
        spinner = self.app.spinner
        steps_run[self.name] = cached
        spinner.succeed(self.messages.past)
        return cached
