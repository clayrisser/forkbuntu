from os import path
from pydash import _
import logging.config
import os
import sys
import yaml

def setup_logger(config_path='logging.yml', name=None, level=logging.INFO, key='LOG_CFG'):
    config_path = path.abspath(os.environ[key] if key in os.environ else config_path)
    config = None
    if path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)
    logger = logging.getLogger()
    if name:
        logger = logging.getLogger(name)
    if _.includes(sys.argv, '--debug') or _.includes(sys.argv, '-d'):
        logger.setLevel(logging.DEBUG)
    return logger
