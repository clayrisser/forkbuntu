from builtins import input
from cfoundation import Service

class HelperService(Service):

    def prompt(self, name, default=None):
        if not default:
            return input(name + ': ')
        result = input(name + ' (' + default + '): ')
        if result and len(result) > 0:
            return result
        return default
