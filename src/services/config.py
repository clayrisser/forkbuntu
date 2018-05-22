from cfoundation import Service
from os import path
from pydash import _
import os
import yaml

class Config(Service):
    def load(self):
        config = {
            'paths': {
                'iso': 'ubuntu-18.04-server-amd64.iso',
                'mount': '.tmp/iso',
                'output': 'forkbuntu.iso',
                'working': os.getcwd()
            },
            'packages': []
        }
        with open(path.abspath('config.yml'), 'r') as f:
            try:
                config = _.merge({}, config, yaml.load(f))
            except yaml.YAMLError as err:
                print(err)
                exit(1)
        return _.merge({}, config, {
            'paths': _.zip_object(
                _.keys(config['paths']),
                _.map(config['paths'], lambda item: path.abspath(path.join(config['paths']['working'], item)))
            )
        })
