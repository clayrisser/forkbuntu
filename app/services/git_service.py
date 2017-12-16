from pydash import _
from os import path
import os
from cfoundation import Service

class GitService(Service):
    def get_email(self):
        email = None
        emails = os.popen('git config --global user.email').read().split('\n')
        if len(emails) > 0:
            email = emails[0]
        return email

    def get_name(self):
        name = None
        names = os.popen('git config --global user.name').read().split('\n')
        if len(names) > 0:
            name = names[0]
        return name
