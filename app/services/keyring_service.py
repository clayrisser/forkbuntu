import os
import re
import gnupg
from os import path
from pydash import _
from app.exceptions.base_exceptions import DefaultException
from pydash import _

gpg = gnupg.GPG(homedir='/root/.gnupg')

def create(name, comment, passphrase, email, basedir=None):
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
        print(key)

def keyfile(name, comment, passphrase, email, basedir=None):
    print('Generating keyfile . . .')
    keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
    if len(keyring) <= 0:
        os.system('apt-get source ubuntu-keyring')
        keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
        if len(keyring) <= 0:
            raise DefaultException('Cannot grab keyring source')
    keyid = get_key_id(name, email)
    os.chdir(keyring + '/keyrings')
    with open('ubuntu-archive-keyring.gpg', 'r') as f:
        gpg.import_keys(f.read())
    keyids = ['FBB75451', '437D05B5', 'C0B21F32', 'EFE21092', keyid]
    keydata_public = gpg.export_keys(keyids)
    keydata_private = gpg.export_keys(keyids, True)
    # with open('ubuntu-archive-keyring.gpg', 'w') as f:
        # f.write(keydata_public)
        # f.write(keydata_private)
        # f.close()
    os.chdir('../')
    # os.system('gpg --list-secret-keys')
    os.system('''
    dpkg-buildpackage -rfakeroot -m"''' + keyid + '''" -k"''' + keyid + '''" -p"gpg2"
    # # cd ..  # you are now on the directory where you started, in the example, /opt/build
    # # cp ubuntu-keyring*deb /opt/cd-image/pool/main/u/ubuntu-keyring
    ''')

def get_key_id(name, email):
    result = os.popen('gpg --list-keys ' + name).read()
    match = re.search('(pub\s+[^\/]+\/)([^\s]+)', result)
    return match.group(2)
