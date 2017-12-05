from pygit import Repository
from pydash import _
from os import path
import os

def get_email():
    repo = Repository(os.getcwd())
    print(_.keys(repo))
