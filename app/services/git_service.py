from pydash import _
from os import path
import os

def get_email():
    email = None
    emails = os.popen('git config --global user.email').read().split('\n')
    if len(emails) > 0:
        email = emails[0]
    return email

def get_name():
    name = None
    names = os.popen('git config --global user.name').read().split('\n')
    if len(names) > 0:
        name = names[0]
    return name
