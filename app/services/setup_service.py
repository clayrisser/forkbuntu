import sys
import os
from app.exceptions.base_exceptions import DefaultException
from os import path

def validate_deps(app):
    app.log.info('Validating build dependencies . . .')
    if is_installed('gpg2'):
        app.log.info('found gpg2')
    else:
        raise DefaultException('gpg required to generate signing keys')

def workdir(workdir):
    if not path.exists(workdir):
        os.mkdir(workdir)

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def is_installed(program):
    res = os.system('which ' + program + ' > /dev/null')
    if res == 0:
        return True
    else:
        return False
