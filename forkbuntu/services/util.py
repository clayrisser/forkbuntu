from cfoundation import Service
from os import path
from subprocess import check_output, CalledProcessError, STDOUT, Popen, DEVNULL
import os
import re
import pwd

class Util(Service):
    def subproc(self, command, real_user=None):
        log = self.app.log
        log.debug('command: ' + command)
        try:
            stdout = ''
            if real_user:
                stdout = self.__demoted_subproc(command)
            else:
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

    def __demoted_subproc(self, command):
        pargs = self.app.pargs
        f = DEVNULL
        if pargs.debug:
            f = None
        command = command.split()
        user = self.get_real_user()
        cwd = os.getcwd()
        pw = pwd.getpwnam(user)
        env = os.environ.copy()
        env['HOME']  = pw.pw_dir
        env['LOGNAME']  = pw.pw_name
        env['PWD']  = cwd
        env['USER']  = pw.pw_name
        proc = Popen(
            command,
            preexec_fn=self.__demote(pw.pw_uid, pw.pw_gid),
            cwd=cwd,
            env=env,
            stdout=f,
            stderr=f
        )
        return proc.wait()

    def __demote(self, uid, gid):
        def result():
            os.setgid(gid)
            os.setuid(uid)
        return result
