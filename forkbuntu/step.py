from pydash import _

steps_run = []

class Step():
    global steps_run

    def __init__(self, name, app):
        self.name = name
        self.app = app
        self.log = app.log

    def run_required(self):
        steps = self.app.steps
        if not hasattr(self, 'requires'):
            return None
        for required in self.requires:
            if not _.includes(steps_run, required):
                getattr(steps, required).start()

    def checksum(self):
        s = self.app.services
        if not hasattr(self, 'checksum_paths'):
            return False
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
        self.run_required()
        spinner.start(self.messages.present)
        passed = self.checksum()
        if passed:
            self.cached()
            return None
        self.run()
        self.register()
        self.finish()

    def cached(self):
        global steps_run
        spinner = self.app.spinner
        steps_run.append(self.name)
        spinner.warn(self.messages.cache)

    def finish(self):
        global steps_run
        spinner = self.app.spinner
        steps_run.append(self.name)
        spinner.succeed(self.messages.past)
