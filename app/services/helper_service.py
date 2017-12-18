import os
from builtins import input
from cfoundation import Service
from getpass import getpass
from glob import glob
from os import path
from pydash import _

class HelperService(Service):

    def prompt(self, name, default=None, private=False):
        message = name + ': '
        if default:
            message = name + ' (' + default + '): '
        result = None
        if private:
            result = getpass(message)
        else:
            result = input(message)
        if result and len(result) > 0:
            return result
        return default

    def find_image(self, search_path=None):
        default_image = None
        images = glob(path.join(os.getcwd(), '*.iso'))
        if images and len(images) > 0:
            return images[0]
        images =glob(path.join(path.expanduser('~'), 'Downloads', '*.iso'))
        if images and len(images) > 0:
            return images[0]
        return None
