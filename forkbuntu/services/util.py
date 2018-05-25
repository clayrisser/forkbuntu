from cfoundation import Service
from jinja2 import Template
from os import path
from subprocess import check_output, CalledProcessError, STDOUT, Popen, DEVNULL
import os
import pwd
import re

class Util(Service):
    def subproc(self, command, real_user=None):
        log = self.app.log
        if real_user:
            user = self.get_real_user()
            return self.subproc('sudo --preserve-env -u ' + user + ' ' + command)
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
            self.app.spinner.fail('subprocess command failed')
            if err.output:
                log.error(err.output.decode('utf-8'))
            else:
                raise err
            if self.app.pargs.debug:
                raise err
            exit(1)

    def get_real_user(self):
        user = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
        matches = re.findall(r'[^\/]+$', path.expanduser('~'))
        if len(matches) > 0:
            user = matches[0]
        return user

    def chown(self, chown_path):
        chown_path = path.abspath(chown_path)
        user = self.get_real_user()
        self.subproc('chown -R ' + user + ':' + user + ' ' + chown_path)

    def stamp_template(self, template_path, **kwargs):
        template_path = path.abspath(template_path)
        body = ''
        with open(template_path, 'r') as f:
            body = f.read()
        template = Template(body)
        body = template.render(**kwargs) + '\n'
        with open(template_path, 'w') as f:
            f.write(body)
