import os
import sys

def get_settings(settings):
    return {
        'basedir': settings['basedir'],
        'extrasdir': settings['basedir'] + '/MyBuild',
        'seedfile': settings['seedfile'],
        'cdimage': settings['cdimage'],
        'cdsourcedir': settings['basedir'] + '/cdsource',
        'sourcedir': settings['basedir'] + '/source',
        'gpgkeyname': settings['gpgkeyname'],
        'gpgkeycomment': settings['gpgkeycomment'],
        'gpgkeyemail': settings['gpgkeyemail'],
        'gpgkeyphrase': settings['gpgkeyphrase'],
        'mygpgkey': settings['gpgkeyname'] + ' (' + settings['gpgkeycomment'] + ') <' + settings['gpgkeyemail'] + '>',
        'packagelist': settings['basedir'] + '/PackageList',
        'cdname': settings['cdname']
    }

def is_installed(program):
    res = os.system('which ' + program + ' > /dev/null')
    if res == 0:
        return True
    else:
        return False

def check_installed(program, message):
    if not is_installed(program):
        print(message)
        sys.exit(1)

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass
