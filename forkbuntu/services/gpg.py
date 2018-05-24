from cfoundation import Service
from getpass import getuser
from os import path
from munch import Munch
from subprocess import Popen
from time import sleep
import grp
import os
import pwd
import re
import json

class GPG(Service):
    def setup(self):
        s = self.app.services
        gpg_path = path.join(path.expanduser('~'), '.gnupg')
        private_keys_path = path.join(gpg_path, 'private-keys-v1.d')
        os.environ['GPG_TTY'] = s.util.subproc('tty')
        if not path.exists(private_keys_path):
            user = s.util.get_real_user()
            os.makedirs(private_keys_path)
            s.util.subproc('chown -R ' + user + ':' + user + ' ' + gpg_path)
        s.util.subproc('gpgconf --kill gpg-agent', real_user=True)
        s.util.subproc('gpg-agent --daemon --keep-tty --pinentry-program=$(which pinentry-curses)', real_user=True)

    def gen_key(self):
        s = self.app.services
        gpg_path = path.join(path.expanduser('~'), '.gnupg')
        user = s.util.get_real_user()
        s.util.subproc('chown -R ' + user + ':' + user + ' ' + gpg_path)
        s.util.subproc('rngd -r /dev/urandom')
        s.util.subproc('gpg --gen-key', real_user=True)

    def get_keys(self, trying_again=False):
        s = self.app.services
        keys = []
        stdout = s.util.subproc('gpg --keyid-format LONG --list-keys')
        matches = re.split(r'-{4}\n', stdout)
        stdout_keys = []
        if len(matches) > 1:
            stdout_keys = list(filter(None, matches[1].split('\n\n')))
        for stdout_key in stdout_keys:
            key = Munch()
            pubkeyshort = ''
            lines = stdout_key.split('\n')
            if (len(lines) >= 3):
                match = next(re.finditer(r'(pub\s+)(\w+)\/(\w+)\s+([\w-]+)', lines[0]), None)
                if match:
                    key_long = match.groups()[2].strip()
                    pub_key_short = key_long[8:]
                    key.pub = Munch({
                        'cipher': match.groups()[1].strip(),
                        'key': {
                            'long': key_long,
                            'short': pub_key_short,
                        },
                        'date': match.groups()[3].strip()
                    })
                match = next(re.finditer(r'(uid\s+\[\w+]\s+)(.+)(<[^<>]+>)', lines[1]), None)
                if match:
                    email = match.groups()[2].strip()
                    key.name = match.groups()[1].strip()
                    key.email = email[1:len(email) - 1]
                match = next(re.finditer(r'(sub\s+)(\w+)\/(\w+)\s+([\w-]+)', lines[2]), None)
                if match:
                    key_long = match.groups()[2].strip()
                    key.sub = Munch({
                        'cipher': match.groups()[1].strip(),
                        'key': {
                            'long': key_long,
                            'short': key_long[8:],
                        },
                        'date': match.groups()[3].strip()
                    })
            keys.append(key)
        if len(keys) <= 0:
            if trying_again:
                self.app.spinner.fail('failed to load gpg keys')
                exit(1)
            self.gen_key()
            return self.get_keys(trying_again=True)
        return keys
