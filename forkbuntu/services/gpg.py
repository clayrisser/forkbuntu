from cfoundation import Service
from munch import munchify, Munch
from os import path
from pydash import _
from subprocess import check_output, CalledProcessError, STDOUT
import glob
import inquirer
import json
import os
import re
import shutil

class GPG(Service):
    ubuntu_keys = ['FBB75451', '437D05B5', 'C0B21F32', 'EFE21092']

    def setup(self):
        s = self.app.services
        gpg_path = path.join(path.expanduser('~'), '.gnupg')
        private_keys_path = path.join(gpg_path, 'private-keys-v1.d')
        if not path.exists(private_keys_path):
            os.makedirs(private_keys_path)
            self.__chmod_gpg()

    def build_keyring(self):
        c = self.app.conf
        log = self.app.log
        pargs = self.app.pargs
        s = self.app.services
        spinner = self.app.spinner
        if path.isdir(c.paths.keyring):
            shutil.rmtree(c.paths.keyring)
        os.makedirs(c.paths.keyring)
        s.util.chown(c.paths.keyring)
        os.chdir(c.paths.keyring)
        try:
            command = 'apt-get source ubuntu-keyring'
            log.debug('command: ' + command)
            stdout = check_output(
                command,
                stderr=STDOUT,
                shell=True
            ).decode('utf-8')
            log.debug(stdout)
            s.util.chown(c.paths.keyring)
        except CalledProcessError as err:
            matches = re.findall(r'Temporary\sfailure\sresolving', err.output.decode('utf-8'))
            if len(matches) > 0:
                spinner.fail('no internet connection')
            if pargs.debug:
                if err.output:
                    log.error(err.output.decode('utf-8'))
                raise err
            exit(1)
        ubuntu_keyring_path = _.filter(os.listdir(c.paths.keyring), os.path.isdir)
        if len(ubuntu_keyring_path) > 0:
            ubuntu_keyring_path = path.join(c.paths.keyring, ubuntu_keyring_path[0])
        else:
            raise Exception('failed to source ubuntu-keyring')
        keyrings_path = path.join(ubuntu_keyring_path, 'keyrings')
        os.chdir(keyrings_path)
        s.util.subproc('gpg --import < ' + path.join(keyrings_path, 'ubuntu-archive-keyring.gpg'))
        gpg_key = self.get_key()
        s.util.subproc(
            'gpg --export ' + ' '.join(self.ubuntu_keys) + ' '
            + gpg_key.pub.key.short + ' > ' + path.join(keyrings_path, 'ubuntu-archive-keyring.gpg')
        )
        os.chdir(ubuntu_keyring_path)
        stdout = s.util.subproc('cat ' + path.join(keyrings_path, 'ubuntu-archive-keyring.gpg') + ' | sha512sum')
        sha512sum = stdout.split(' ')[0]
        lines = []
        with open(path.join(ubuntu_keyring_path, 'SHA512SUMS.txt.asc'), 'r') as f:
            for line in f.readlines():
                line = re.sub(r'(\w+)(?=\s+keyrings/ubuntu-archive-keyring.gpg)', sha512sum, line)
                lines.append(line)
        with open(path.join(ubuntu_keyring_path, 'SHA512SUMS.txt.asc'), 'w') as f:
            f.writelines(lines)
        self.app.spinner.stop()
        s.util.subproc(
            'dpkg-buildpackage -rfakeroot -m"' + gpg_key.name + ' <' + gpg_key.email + '>" -k'
            + gpg_key.pub.key.short
        )
        self.app.spinner.start()
        keyring_deb_path = _.filter(os.listdir(c.paths.keyring), lambda x: x[len(x) - 4:] == '.deb')
        if len(keyring_deb_path) > 0:
            keyring_deb_path = path.join(c.paths.keyring, keyring_deb_path[0])
        else:
            raise Exception('failed to build ubuntu-keyring')
        for deb_path in glob.glob(path.join(c.paths.keyring, 'ubuntu-keyring*deb')):
            shutil.copy(deb_path, path.join(c.paths.mount, 'pool/main/u/ubuntu-keyring'))
        if not path.isdir(path.join(c.paths.filesystem, 'var/lib/apt/keyrings')):
            os.makedirs(path.join(c.paths.filesystem, 'var/lib/apt/keyrings'))
        if not path.isdir(path.join(c.paths.filesystem, 'etc/apt')):
            os.makedirs(path.join(c.paths.filesystem, 'etc/apt'))
        if not path.isdir(path.join(c.paths.filesystem, 'var/lib/apt/keyrings')):
            os.makedirs(path.join(c.paths.filesystem, 'var/lib/apt/keyrings'))
        shutil.copyfile(keyring_deb_path, path.join(c.paths.filesystem, 'usr/share/keyrings/ubuntu-archive-keyring.gpg'))
        shutil.copyfile(keyring_deb_path, path.join(c.paths.filesystem, 'etc/apt/trusted.gpg'))
        shutil.copyfile(keyring_deb_path, path.join(c.paths.filesystem, 'var/lib/apt/keyrings/ubuntu-archive-keyring.gpg'))
        os.chdir(c.paths.cwd)

    def gen_key(self):
        s = self.app.services
        spinner = self.app.spinner
        self.__chmod_gpg()
        s.util.subproc('rngd -r /dev/urandom', sudo=True)
        spinner.stop()
        s.util.subproc('gpg --gen-key')
        spinner.start()

    def get_keys(self, include_ubuntu_keys=False, trying_again=False):
        s = self.app.services
        keys = []
        stdout = s.util.subproc('gpg --keyid-format LONG --list-keys')
        matches = re.split(r'-{4}\n', stdout)
        stdout_keys = []
        if len(matches) > 1:
            stdout_keys = list(filter(None, matches[1].split('\n\n')))
        for stdout_key in stdout_keys:
            key = Munch()
            lines = stdout_key.split('\n')
            if (len(lines) >= 2):
                match = next(re.finditer(r'(pub\s+)(\w+)\/(\w+)\s+([\w-]+)', lines[0]), None)
                if match:
                    key_long = match.groups()[2].strip()
                    pub_key_short = key_long[8:]
                    key.pub = munchify({
                        'cipher': match.groups()[1].strip(),
                        'key': {
                            'long': key_long,
                            'short': pub_key_short,
                        },
                        'date': match.groups()[3].strip()
                    })
                match = next(re.finditer(r'(uid\s+\[.+]\s+)(.+)(<[^<>]+>)', lines[1]), None)
                if match:
                    email = match.groups()[2].strip()
                    key.name = match.groups()[1].strip()
                    key.email = email[1:len(email) - 1]
            if (len(lines) >= 3):
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
            if not ('pub' in key and 'name' in key and 'email' in key):
                continue
            if not include_ubuntu_keys:
                if _.includes(self.ubuntu_keys, key.pub.key.short):
                    continue
            keys.append(key)
        if len(keys) <= 0:
            if trying_again:
                self.app.spinner.fail('failed to load gpg keys')
                exit(1)
            self.gen_key()
            return self.get_keys(trying_again=True)
        return keys

    def get_key(self):
        c = self.app.conf
        spinner = self.app.spinner
        gpg_keys = self.app.gpg_keys
        gpg_key = None
        if len(gpg_keys) == 1:
            gpg_key = gpg_keys[0]
        elif len(gpg_keys) > 1:
            spinner.stop()
            answer = munchify(inquirer.prompt([
                inquirer.List(
                    'gpg_key',
                    message='choose a gpg key',
                    choices=_.map(gpg_keys, lambda x: x.pub.key.short + ': ' + x.name + ' <' + x.email + '>')
                )
            ])).gpg_key
            spinner.start()
            gpg_key = _.find(gpg_keys, lambda x: x.pub.key.short == answer[:answer.index(':')])
        if not gpg_key:
            raise Exception('failed to find gpg key')
        return gpg_key

    def __chmod_gpg(self):
        s = self.app.services
        user = s.util.get_real_user()
        gpg_path = path.join(path.expanduser('~'), '.gnupg')
        s.util.chown(gpg_path)
        s.util.subproc('chmod 700 ' + gpg_path, sudo=True)
        s.util.subproc('find ' + gpg_path + ' -type f -exec chmod 600 {} \;', sudo=True)
