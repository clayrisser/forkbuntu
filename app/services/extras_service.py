import os
from os import path
from distutils.dir_util import copy_tree
from jinja2 import Template
from cfoundation import Service

class ExtrasService(Service):

    def copy(self, extras, workdir):
        s = self.app.services
        s.task_service.started('copy_extras')
        contents_path = path.join(workdir, 'contents')
        if not path.exists(contents_path + '/pool/extras'):
            os.makedirs(contents_path + '/pool/extras')
        copy_tree(extras, path.join(contents_path, 'pool', 'extras'))
        s.task_service.finished('copy_extras')

    def build_repository(self,workdir, name, dist):
        s = self.app.services
        s.task_service.started('build_repository')
        indices_path = path.join(workdir, 'indices')
        ftp_archive_src_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), '..', 'apt-ftparchive'))
        ftp_archive_dest_path = path.join(workdir, 'apt-ftparchive')
        contents_path = path.join(workdir, 'contents')
        if not path.exists(indices_path):
            os.mkdir(indices_path)
        os.chdir(indices_path)
        suffixes = [
            'extra.main',
            'main',
            'main.debian-installer',
            'restricted',
            'restricted.debian-installer'
        ]
        for suffix in suffixes:
            if not path.exists(path.join(indices_path, 'override.' + dist + '.' + suffix)):
                os.popen('wget http://archive.ubuntu.com/ubuntu/indices/override.' + dist + '.' + suffix)
        if not path.exists(ftp_archive_dest_path):
            os.mkdir(ftp_archive_dest_path)
        context = {
            'workdir': workdir,
            'dist': dist
        }
        self.write_conf(
            source=path.join(ftp_archive_src_path, 'apt-ftparchive-dev.conf'),
            destination=path.join(ftp_archive_dest_path, 'apt-ftparchive-dev.conf'),
            context=context
        )
        self.write_conf(
            source=path.join(ftp_archive_src_path, 'apt-ftparchive-extras.conf'),
            destination=path.join(ftp_archive_dest_path, 'apt-ftparchive-extras.conf'),
            context=context
        )
        self.write_conf(
            source=path.join(ftp_archive_src_path, 'apt-ftparchive-udeb.conf'),
            destination=path.join(ftp_archive_dest_path, 'apt-ftparchive-udeb.conf'),
            context=context
        )
        self.write_conf(
            source=path.join(ftp_archive_src_path, 'release.conf'),
            destination=path.join(ftp_archive_dest_path, 'release.conf'),
            context=context
        )
        os.chdir(contents_path)
        if not path.exists(path.join(contents_path, 'dists/stable/extras/binary-amd64')):
            os.makedirs(path.join(contents_path, 'dists/stable/extras/binary-amd64'))
        os.system('''
        apt-ftparchive packages pool/extras > dists/stable/extras/binary-amd64/Packages
        gzip -c dists/stable/extras/binary-amd64/Packages | tee dists/stable/extras/binary-amd64/Packages.gz > /dev/null
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-deb.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-udeb.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-extras.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf release ''' + contents_path + '''/dists/''' + dist + ''' > ''' + contents_path + '''/dists/''' + dist + '''/Release
        gpg --default-key "''' + name + '''" --output ''' + contents_path + '''/dists/''' + dist + '''/Release.gpg -ba ''' + contents_path + '''/dists/''' + dist + '''/Release
        find \. -type f -print0 | xargs -0 md5sum > tee md5sum.txt
        ''')
        os.chdir(workdir)
        s.task_service.finished('build_repository')

    def write_conf(self, source, destination, context):
        s = self.app.services
        s.task_service.started('write_conf')
        result = ''
        with open(source, 'r') as f:
            t = Template(f.read())
            result = t.render(context)
            f.close()
        with open(destination, 'w') as f:
            f.write(result)
            f.close()
        s.task_service.finished('write_conf')
