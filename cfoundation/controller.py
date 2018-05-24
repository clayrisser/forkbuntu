from cement.core.controller import CementBaseController

class Controller(CementBaseController):
    def init(self):
        self.log = self.app.log
