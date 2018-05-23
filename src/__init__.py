from . import controllers, services
from cfoundation import create_app
from os import path
from pydash import _
from tempfile import gettempdir
import os
import yaml

def load_config(config):
    with open(path.abspath('config.yml'), 'r') as f:
        try:
            config = _.merge({}, config, yaml.load(f))
        except yaml.YAMLError as err:
            print(err)
            exit(1)
    return _.merge({}, config, {
        'paths': _.zip_object(
            _.keys(config['paths']),
            _.map(config['paths'], lambda item: path.abspath(path.join(config['paths']['cwd'], item)))
        )
    })

App = create_app(
    controllers=controllers,
    services=services,
    config=load_config({
        'name': 'Forkbuntu',
        'packages': [],
        'paths': {
            'cwd': os.getcwd(),
            'iso': 'ubuntu-18.04-server-amd64.iso',
            'mount': '.tmp/iso',
            'output': 'forkbuntu.iso',
            'src': path.dirname(path.realpath(__file__)),
            'tmp': gettempdir()
        }
    })
)
