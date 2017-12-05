from builtins import input

def prompt(name, default=None):
    if not default:
        return input(name + ': ')
    result = input(name + ' (' + default + '): ')
    if result and len(result) > 0:
        return result
    return default
