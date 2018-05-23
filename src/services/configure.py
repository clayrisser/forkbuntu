from cfoundation import Service
from distutils.dir_util import copy_tree
from jinja2 import Template
from os import path
import os

class Configure(Service):
    def merge_files(self):
        c = self.app.conf
        copy_tree(path.join(c.paths.src, 'iso'), c.paths.mount)
        self.__stamp_template(path.join(c.paths.mount, 'preseed', 'forkbuntu.seed'), packages=c.packages)
        self.__stamp_template(path.join(c.paths.mount, '.disk', 'info'), packages=c.packages)
        if path.isdir(path.join(c.paths.cwd, 'scripts')):
            copy_tree(path.join(c.paths.cwd, 'scripts'), path.join(c.paths.mount, 'scripts'))
        if path.isdir(path.join(c.paths.cwd, 'iso')):
            copy_tree(path.join(c.paths.cwd, 'iso'), c.paths.mount)

    def sign(self):
        c = self.app.conf
        os.system('cd ' + c.paths.mount + ''' && \
        find . -path ./isolinux -prune -o  -path ./md5sum.txt -prune -o -type f -print0 | \
        xargs -0 md5sum > md5sum.txt
        ''')

    def __stamp_template(self, template_path, **kwargs):
        template_path = path.abspath(template_path)
        body = ''
        with open(template_path, 'r') as f:
            body = f.read()
        template = Template(body)
        body = template.render(**kwargs) + '\n'
        with open(template_path, 'w') as f:
            f.write(body)
