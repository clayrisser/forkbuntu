from cfoundation import Service
from jinja2 import Template
from os import path
from subprocess import check_output, CalledProcessError, STDOUT
import os
import re

class Util(Service):
    def subproc(self, command, sudo=False):
        log = self.app.log
        pargs = self.app.pargs
        spinner = self.app.spinner
        if not sudo:
            user = self.get_real_user()
            return self.subproc('sudo --preserve-env -u ' + user + ' ' + command, sudo=True)
        log.debug('command: ' + command)
        try:
            stdout = check_output(
                command,
                stderr=STDOUT,
                shell=True
            ).decode('utf-8')
            log.debug(stdout)
            return stdout
        except CalledProcessError as err:
            spinner.fail('subprocess command failed')
            if err.output:
                log.error(err.output.decode('utf-8'))
            else:
                raise err
            if self.app.pargs.debug:
                raise err
            exit(1)

    def get_real_user(self):
        user = os.environ['SUDO_USER']
        if not user:
            matches = re.findall(r'[^\/]+$', path.expanduser('~'))
            if len(matches) > 0:
                user = matches[0]
            else:
                user = os.environ['USER']
        return user

    def chown(self, chown_path, user=None):
        chown_path = path.abspath(chown_path)
        if not user:
            user = self.get_real_user()
        self.subproc('chown -R ' + user + ':' + user + ' ' + chown_path, sudo=True)

    def stamp_template(self, template_path, **kwargs):
        template_path = path.abspath(template_path)
        body = ''
        with open(template_path, 'r') as f:
            body = f.read()
        template = Template(body)
        body = template.render(**kwargs) + '\n'
        with open(template_path, 'w') as f:
            f.write(body)

    def download(self, url, output_path):
        log = self.app.log
        output_path = path.abspath(output_path)
        pargs = self.app.pargs
        spinner = self.app.spinner
        try:
            command = 'curl -L -o ' + output_path + ' ' + url
            log.debug('command: ' + command)
            stdout = check_output(
                command,
                stderr=STDOUT,
                shell=True
            ).decode('utf-8')
            log.debug(stdout)
            self.chown(output_path)
            return stdout
        except CalledProcessError as err:
            matches = re.findall(r'Couldn\'t\sconnect\sto\sserver', err.output.decode('utf-8'))
            if len(matches) > 0:
                spinner.fail('no internet connection')
            if pargs.debug:
                if err.output:
                    log.error(err.output.decode('utf-8'))
                raise err
            exit(1)
