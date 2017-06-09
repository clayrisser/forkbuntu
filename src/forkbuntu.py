#!/usr/bin/env python

import os
import re
import sys
import os.path
from pkg import helpers, jobs
from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults

if not os.geteuid() == 0:
    print('Script must be run as root')
    sys.exit(1)

settings = {
    'basedir': os.getcwd() + '/MyBuildInstall',
    'seedfile': 'mybuild.seed',
    'cdimage': 'ubuntu-5.10-install-i386.iso',
    'gpgkeyname': 'My Organisation Installation Key',
    'gpgkeycomment': 'Package Signing',
    'gpgkeyemail': 'myorg@myorganisation.com',
    'gpgkeyphrase': 'MyOrg',
    'cdname': 'MyBuild.iso'
}
settings = helpers.get_settings(settings)

defaults = init_defaults('auth-sheep')
defaults['auth-sheep']['debug'] = False

class AuthSheep(CementApp):
    class Meta:
        label = 'auth-sheep'
        config_defaults = defaults

def main(argv):
    with AuthSheep() as app:
        app.run()
        helpers.check_installed('gpg', 'Please install gpg to generate signing keys')
        jobs.mkdirs(settings)
        if not os.path.isfile(settings['basedir'] + '/' + settings['cdimage']):
            print('Cannot find your ubuntu image. Change \'cdimage\' path.')
            sys.exit(1)
        jobs.keyring(settings)
        jobs.mountiso(settings)
        jobs.ftparchive(settings)
        jobs.resync(settings)
        jobs.remove_packages(settings)
        jobs.keyfile(settings)

main(sys.argv)
