from cfoundation import Service
from os import path
from pydash import _
import yaml

class Config(Service):
    def load(self):
        config = {
            'paths': {
                'iso': 'ubuntu-18.04-server-amd64.iso',
                'mount': '.tmp/mount',
                'output': 'forkbuntu.iso'
            }
        }
        with open(path.abspath('config.yml'), 'r') as f:
            try:
                config = _.merge({}, config, yaml.load(f))
            except yaml.YAMLError as err:
                print(err)
                exit(1)
        return config
