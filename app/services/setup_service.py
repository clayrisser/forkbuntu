import sys
import os
from app.exceptions.base_exceptions import DefaultException
from os import path

def validate_deps():
    print('validating deps . . .')
    if not is_installed('gpg'):
        raise DefaultException('gpg required to generate signing keys')

def validate_image(image_name):
    print('validating image . . .')
    image_path = path.abspath(path.join(image_name))
    if not os.path.isfile(image_name):
        raise DefaultException(image_path + ' is not a valid ubuntu image')

def basedir(basedir, cdsourcedir, extrasdir, sourcedir):
    mkdir(basedir)
    mkdir(basedir + '/FinalCD')
    mkdir(cdsourcedir)
    mkdir(extrasdir)
    mkdir(extrasdir + '/preseed')
    mkdir(extrasdir + '/pool/extras')
    mkdir(sourcedir)
    mkdir(sourcedir + '/keyring')
    mkdir(sourcedir + '/indices')
    mkdir(sourcedir + '/ubuntu-meta')

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
