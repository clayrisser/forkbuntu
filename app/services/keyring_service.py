import os
import re
from app.exceptions.base_exceptions import DefaultException
from pydash import _

def create(name, comment, passphrase, email, basedir=None):
    if not basedir:
        basedir = os.getcwd()
    response = os.system('gpg2 --list-keys | grep "'+ name + '" >/dev/null')
    if response != 0:
        print('No GPG Key found in your keyring.')
        print('Generating a new gpg key (' + name + ' ' + comment + ') with a passphrase of ' + passphrase + ' . . .')
        with open(basedir + '/key.inc', 'w') as f:
            f.write('''Key-Type: DSA
Key-Length: 1024
Subkey-Type: ELG-E
Subkey-Length: 2048
Name-Real: ''' + name + '''
Name-Comment: ''' + comment + '''
Name-Email: ''' + email + '''
Expire-Date: 0
Passphrase: ''' + passphrase + '''\n''')
        os.system('gpg2 --gen-key --batch --gen-key ' + basedir + '/key.inc')

def keyfile(name, comment, passphrase, email, basedir=None):
    print('Generating keyfile . . .')
    keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
    if len(keyring) <= 0:
        os.system('apt-get source ubuntu-keyring')
        keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read().split('\n')[0]
        if len(keyring) <= 0:
            raise DefaultException('Cannot grab keyring source')
    key_id = get_key_id(name)
    os.chdir(keyring + '/keyrings')
    print(key_id)
    os.system('''
    gpg2 --import < ubuntu-archive-keyring.gpg
    gpg2 --export FBB75451 437D05B5 C0B21F32 EFE21092 ''' + key_id + ''' > ubuntu-archive-keyring.gpg
    cd ..    # you are now on ubuntu-keyring-2012.05.19
    # dpkg-buildpackage -rfakeroot -m"Your Name <''' + email + '>" -k' + key_id + ''' -p'gpg --no-tty --passphrase ''' + passphrase + ''''
    # cd ..  # you are now on the directory where you started, in the example, /opt/build
    # cp ubuntu-keyring*deb /opt/cd-image/pool/main/u/ubuntu-keyring
    ''')

def get_key_id(keyname):
    result = os.popen('gpg2 --list-keys ' + keyname).read()
    match = re.search('(pub\s+[^\/]+\/)([^\s]+)', result)
    return match.group(2)
