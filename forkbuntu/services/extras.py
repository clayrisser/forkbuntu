from cfoundation import Service

class Extras(Service):
    def create(self):
        log = self.app.log
        c = self.app.conf
        log.info('howdy')
