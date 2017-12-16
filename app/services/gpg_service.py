import os
import re
import gnupg
from shutil import copyfile
from os import path
from pydash import _
from app.exceptions.base_exceptions import DefaultException
from pydash import _
from cfoundation import Service

gpg = gnupg.GPG(homedir=path.join(path.expanduser('~'), '.gnupg'))

class GpgService(Service):

    def create(self, name, comment, passphrase, email):
        log = self.app.log
        log.info('^ started gpg create')
        keys = gpg.list_keys()
        key_exists = False
        for key in keys:
            if (name + ' <' + email + '>') == _.keys(key['sigs'])[0]:
                key_exists = True
        if not key_exists:
            input_data = gpg.gen_key_input(
                key_type='RSA',
                key_length=1024,
                subkey_type='ELG-E',
                subkey_length=2048,
                name_real=name,
                name_email=email,
                expire_date=0,
                passphrase=passphrase
            )
            key = gpg.gen_key(input_data)
        log.info('$ finished gpg create')

    def generate_keyfile(self, name, comment, passphrase, email, workdir):
        log = self.app.log
        log.info('^ started gpg generate keyfile')
        keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
        if len(keyring) <= 0:
            os.popen('apt-get source ubuntu-keyring').read()
            keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
            if len(keyring) <= 0:
                raise DefaultException('Cannot grab keyring source')
        keyid = self.get_key_id(name, email)
        os.chdir(path.join(keyring, 'keyrings'))
        if not path.exists('ubuntu-archive-keyring-original.gpg'):
            os.rename('ubuntu-archive-keyring.gpg', 'ubuntu-archive-keyring-original.gpg')
        with open('ubuntu-archive-keyring-original.gpg', 'r') as f:
            gpg.import_keys(f.read())
        keyids = ['FBB75451', '437D05B5', 'C0B21F32', 'EFE21092', keyid]
        keydata_public = gpg.export_keys(keyids)
        keydata_private = gpg.export_keys(keyids, True)
        with open('ubuntu-archive-keyring.gpg', 'w') as f:
            f.write(keydata_public)
            f.write(keydata_private)
            f.close()
        os.chdir(path.abspath('..'))
        os.system('dpkg-buildpackage -rfakeroot -m"' + keyid + '" -k"' + keyid + '"')
        keyfile = path.join(os.getcwd(), 'keyrings', 'ubuntu-archive-keyring.gpg')
        copyfile(keyfile, path.join(workdir, 'filesystem/etc/apt/trusted.gpg'))
        copyfile(keyfile, path.join(workdir, 'filesystem/usr/share/keyrings/ubuntu-archive-keyring.gpg'))
        copyfile(keyfile, path.join(workdir, 'filesystem/var/lib/apt/keyrings/ubuntu-archive-keyring.gpg'))
        log.info('$ finished gpg generate keyfile')

    def get_key_id(self, name, email):
        result = os.popen('gpg --list-keys ' + name).read()
        match = re.search('(pub\s+[^\/]+\/)([^\s]+)', result)
        return match.group(2)
