from . import controllers, services, steps
from cfoundation import create_app
from munch import munchify
from os import path
from pydash import _
from tempfile import mkdtemp
from halo import Halo
import os
import re
import sys
import yaml

def get_steps(app):
    context = Object()
    for key in dir(steps):
        matches = re.findall(r'[A-Z].*', key)
        if len(matches) > 0:
            name = _.snake_case(key)
            setattr(context, name, getattr(steps, key)(name, app))
    return context

def load_conf(conf):
    if _.includes(sys.argv, '-h') or _.includes(sys.argv, '--help'):
        return conf
    cwd_path = os.getcwd()
    flag = None
    if _.includes(sys.argv, '--source'):
        flag = '--source'
    elif _.includes(sys.argv, '--src'):
        flag = '--src'
    elif _.includes(sys.argv, '-s'):
        flag = '-s'
    if flag:
        flag_index = _.index_of(sys.argv, flag)
        if len(sys.argv) > flag_index + 1:
            cwd_path = path.abspath(sys.argv[flag_index + 1])
    config_path = path.join(cwd_path, 'config.yml')
    if not path.exists(config_path):
        Halo(text='config not found: ' + config_path).fail()
        exit(1)
    with open(config_path, 'r') as f:
        try:
            conf = munchify(_.merge({}, conf, yaml.load(f)))
        except yaml.YAMLError as err:
            print(err)
            exit(1)
    conf.paths.cwd = cwd_path
    if 'version' in conf:
        conf.version = str(conf.version)
    conf.paths.install = path.join(conf.paths.mount, 'casper')
    if not path.exists(path.join(conf.paths.install, 'filesystem.squashfs')):
        conf.paths.install = path.join(conf.paths.mount, 'install')
    output_path = conf.paths.output
    conf = munchify(_.merge({}, conf, {
        'paths': _.zip_object(
            _.keys(conf.paths),
            _.map(conf.paths, lambda x: path.abspath(path.join(conf.paths.cwd, x)))
        )
    }))
    conf.paths.output = path.abspath(output_path)
    return conf

App = create_app(
    name='forkbuntu',
    controllers=controllers,
    services=services,
    conf=load_conf({
        'apt': {
            'restricted': True,
            'universe': True,
            'multiarch': True
        },
        'debug': _.includes(sys.argv, '--debug'),
        'filesystem': {
            'compress': False
        },
        'packages': [],
        'paths': {
            'apt_ftparchive': '.tmp/apt-ftparchive',
            'cwd': os.getcwd(),
            'cwt': '.tmp',
            'filesystem': '.tmp/filesystem',
            'indices': '.tmp/indices',
            'iso': 'ubuntu-18.04-server-amd64.iso',
            'keyring': '.tmp/keyring',
            'initrd': '.tmp/initrd',
            'mount': '.tmp/iso',
            'output': 'forkbuntu.iso',
            'src': path.dirname(path.realpath(__file__)),
            'tmp': mkdtemp()
        }
    })
)

class Object():
    pass
