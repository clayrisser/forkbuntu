from cement.core.controller import CementBaseController, expose
from app.services import setup_service, keyring_service, image_service
from os import path
import os

class BuildController(CementBaseController):
    class Meta:
        label = 'build'
        description = 'Build Ubuntu'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-i', '--image'], {
                'action': 'store',
                'dest': 'image',
                'help': 'Image location',
                'required': True
            }),
            (['-e', '--email'], {
                'action': 'store',
                'dest': 'email',
                'help': 'Email',
                'required': True
            }),
            (['--key-name'], {
                'action': 'store',
                'dest': 'key_name',
                'help': 'Key name',
                'required': True
            }),
            (['--key-comment'], {
                'action': 'store',
                'dest': 'key_comment',
                'help': 'Key comment',
                'required': True
            }),
            (['--key-passphrase'], {
                'action': 'store',
                'dest': 'key_passphrase',
                'help': 'Key passphrase',
                'required': True
            }),
            (['-b', '--basedir'], {
                'action': 'store',
                'dest': 'basedir',
                'help': 'Base directory',
                'required': True
            })
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs
        image = path.abspath(path.join(os.getcwd(), pargs.image))
        basedir = path.abspath(path.join(os.getcwd(), pargs.basedir))
        cdsourcedir = path.abspath(path.join(basedir, 'cdsource'));
        extrasdir = path.abspath(path.join(basedir, 'MyBuild'))
        sourcedir = path.abspath(path.join(basedir, 'source'));
        setup_service.validate_deps()
        setup_service.validate_image(image)
        setup_service.basedir(basedir, cdsourcedir, extrasdir, sourcedir)
        os.chdir(basedir)
        keyring_service.create(pargs.key_name, pargs.key_comment, pargs.key_passphrase, pargs.email, basedir)
        image_service.mountiso(cdsourcedir, basedir, image)
        image_service.clone_iso_contents(basedir, cdsourcedir)
        image_service.unmountiso(cdsourcedir)
        keyring_service.keyfile(pargs.key_name, pargs.key_comment, pargs.key_passphrase, pargs.email, basedir)
