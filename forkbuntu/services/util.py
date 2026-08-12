from __future__ import annotations

import os
import re
from os import path
from subprocess import STDOUT, CalledProcessError, check_output

from jinja2 import Template

from ..service import Service


class Util(Service):
    def subproc(self, command: str | list[str], sudo: bool = False) -> str:
        """Run a command, de-escalating to the invoking user by default.

        The app runs as root; ``sudo=True`` keeps root privileges while the
        default re-runs the command as the user who invoked sudo. When the
        invoking user is already root (e.g. inside a container) no sudo
        wrapper is needed.
        """
        c = self.app.conf
        log = self.app.log
        spinner = self.app.spinner
        if not sudo:
            user = self.get_real_user()
            if user != "root":
                if isinstance(command, str):
                    command = "sudo --preserve-env -u " + user + " " + command
                else:
                    command = ["sudo", "--preserve-env", "-u", user] + command
            return self.subproc(command, sudo=True)
        log.debug("command: " + self._render_command(command))
        try:
            stdout = check_output(
                command,
                stderr=STDOUT,
                shell=isinstance(command, str),
            ).decode("utf-8")
            log.debug(stdout)
            return stdout
        except CalledProcessError as err:
            spinner.fail("subprocess command failed")
            if err.output:
                log.error(err.output.decode("utf-8"))
            if c.debug:
                raise err
            raise SystemExit(1) from err

    def get_real_user(self) -> str:
        user = os.environ.get("SUDO_USER")
        if not user:
            matches = re.findall(r"[^\/]+$", path.expanduser("~"))
            if len(matches) > 0:
                user = matches[0]
            else:
                user = os.environ["USER"]
        return user

    def chown(self, chown_path: str, user: str | None = None) -> None:
        chown_path = path.abspath(chown_path)
        if not user:
            user = self.get_real_user()
        if user == "root":
            return
        self.subproc(["chown", "-R", user + ":" + user, chown_path], sudo=True)

    def stamp_template(self, template_path: str, **kwargs: object) -> None:
        template_path = path.abspath(template_path)
        with open(template_path) as f:
            body = f.read()
        template = Template(body)
        body = template.render(**kwargs) + "\n"
        with open(template_path, "w") as f:
            f.write(body)

    def download(self, url: str, output_path: str) -> str:
        c = self.app.conf
        log = self.app.log
        output_path = path.abspath(output_path)
        spinner = self.app.spinner
        command = ["curl", "-fsSL", "-o", output_path, url]
        log.debug("command: " + self._render_command(command))
        try:
            stdout = check_output(command, stderr=STDOUT).decode("utf-8")
            log.debug(stdout)
            self.chown(output_path)
            return stdout
        except CalledProcessError as err:
            output = err.output.decode("utf-8") if err.output else ""
            if re.search(r"Could(n't| not)\s(connect|resolve)", output):
                spinner.fail("no internet connection")
            if c.debug:
                if output:
                    log.error(output)
                raise err
            raise SystemExit(1) from err

    def _render_command(self, command: str | list[str]) -> str:
        if isinstance(command, str):
            return command
        return " ".join(command)
