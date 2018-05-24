from . import controllers, services
from cfoundation import create_app
from os import path
from pydash import _
from tempfile import mkdtemp
import os
import yaml
from munch import munchify

def load_conf(conf):
    with open(path.abspath('config.yml'), 'r') as f:
        try:
            conf = munchify(_.merge({}, conf, yaml.load(f)))
        except yaml.YAMLError as err:
            print(err)
            exit(1)
    if 'version' in conf:
        conf.version = str(conf.version)
    conf.paths.install = path.join(conf.paths.mount, 'casper')
    if not path.exists(path.join(conf.paths.install, 'filesystem.squashfs')):
        conf.paths.install = path.join(conf.paths.mount, 'install')
    return munchify(_.merge({}, conf, {
        'paths': _.zip_object(
            _.keys(conf.paths),
            _.map(conf.paths, lambda item: path.abspath(path.join(conf.paths.cwd, item)))
        )
    }))

App = create_app(
    name='forkbuntu',
    controllers=controllers,
    services=services,
    conf=load_conf({
        'filesystem': {
            'compress': False
        },
        'packages': [],
        'paths': {
            'cwd': os.getcwd(),
            'filesystem': '.tmp/filesystem',
            'iso': 'ubuntu-18.04-server-amd64.iso',
            'mount': '.tmp/iso',
            'output': 'forkbuntu.iso',
            'src': path.dirname(path.realpath(__file__)),
            'tmp': mkdtemp()
        }
    })
)
