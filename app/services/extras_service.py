import os
from getpass import getuser
from os import path
from distutils.dir_util import copy_tree
from jinja2 import Template
from cfoundation import Service

class ExtrasService(Service):

    def copy(self, extras_path, workdir):
        s = self.app.services
        s.task_service.started('copy_extras')
        contents_path = path.join(workdir, 'contents')
        os.system('sudo mkdir -p ' + contents_path + '/pool/extras')
        if not path.exists(extras_path):
            os.makedirs(extras_path)
        os.system('sudo rsync -a ' + extras_path + '/ ' + path.join(contents_path, 'pool', 'extras'))
        os.popen('sudo chown -R ' + getuser() + ':' + getuser() + ' ' + path.join(contents_path, 'pool', 'extras'))
        s.task_service.finished('copy_extras')

    def build_repository(self, workdir, name, passphrase, dist):
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
                os.system('wget http://archive.ubuntu.com/ubuntu/indices/override.' + dist + '.' + suffix)
        if not path.exists(ftp_archive_dest_path):
            os.mkdir(ftp_archive_dest_path)
        context = {
            'workdir': workdir,
            'dist': dist
        }
        self.write_conf(
            source=path.join(ftp_archive_src_path, 'apt-ftparchive-deb.conf'),
            destination=path.join(ftp_archive_dest_path, 'apt-ftparchive-deb.conf'),
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
        os.system('sudo mkdir -p ' + path.join(contents_path, 'dists/stable/extras/binary-amd64'))
        os.system('''
        sudo apt-ftparchive packages pool/extras | sudo tee dists/stable/extras/binary-amd64/Packages > /dev/null
        sudo gzip -c dists/stable/extras/binary-amd64/Packages | sudo tee dists/stable/extras/binary-amd64/Packages.gz > /dev/null
        sudo apt-ftparchive -c ''' + ftp_archive_dest_path + '/release.conf generate ' + ftp_archive_dest_path + '''/apt-ftparchive-deb.conf
        sudo apt-ftparchive -c ''' + ftp_archive_dest_path + '/release.conf generate ' + ftp_archive_dest_path + '''/apt-ftparchive-udeb.conf
        sudo apt-ftparchive -c ''' + ftp_archive_dest_path + '/release.conf generate ' + ftp_archive_dest_path + '''/apt-ftparchive-extras.conf
        sudo apt-ftparchive -c ''' + ftp_archive_dest_path + '/release.conf release ' + contents_path + '/dists/' + dist + ' | sudo tee ' + contents_path + '/dists/' + dist + '''/Release > /dev/null
        ''')
        os.system('''
        (echo ''' + passphrase + ') | sudo gpg2 --batch --yes --passphrase-fd 0 --default-key "' + name + '''" \
        --output ''' + path.join(contents_path, 'dists', dist, 'Release.gpg') + ' -ba ' + path.join(contents_path, 'dists', dist, 'Release') + '''
        ''')
        os.popen('sudo chown -R ' + getuser() + ':' + getuser() + ' ' + path.join(contents_path, 'dists'))
        md5sum = os.popen('find \. -type f -print0 | xargs -0 md5sum').read()
        os.popen('echo ' + md5sum + ' | sudo tee ' + path.join(contents_path, 'md5sum.txt')).read()
        os.chdir(workdir)
        s.task_service.finished('build_repository')

    def write_conf(self, source, destination, context):
        s = self.app.services
        result = ''
        with open(source, 'r') as f:
            t = Template(f.read())
            result = t.render(context)
            f.close()
        with open(destination, 'w') as f:
            f.write(result)
            f.close()
