import os
from os import path
from distutils.dir_util import copy_tree
from jinja2 import Template
from cfoundation import Service

class ExtrasService(Service):

    def copy(self, extras, workdir):
        log = self.app.log
        log.info('^ started extras copy')
        contents_path = path.join(workdir, 'contents')
        os.popen('sudo mkdir -p ' + contents_path + '/pool/extras').read()
        copy_tree(extras, path.join(contents_path, 'pool', 'extras'))
        log.info('$ finished extras copy')

    def build_repository(self,workdir, name, dist):
        log = self.app.log
        log.info('^ started extras build repository')
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
        os.system('''
        apt-ftparchive packages pool/extras > dists/stable/extras/binary-amd64/Packages
        gzip -c dists/stable/extras/binary-amd64/Packages | tee dists/stable/extras/binary-amd64/Packages.gz > /dev/null
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-deb.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-udeb.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf generate ''' + ftp_archive_dest_path + '''/apt-ftparchive-extras.conf
        apt-ftparchive -c ''' + ftp_archive_dest_path + '''/release.conf release ''' + contents_path + '''/dists/''' + dist + ''' > ''' + contents_path + '''/dists/''' + dist + '''/Release
        gpg --default-key "''' + name + '''" --output ''' + contents_path + '''/dists/''' + dist + '''/Release.gpg -ba ''' + contents_path + '''/dists/''' + dist + '''/Release
        find \. -type f -print0 | xargs -0 md5sum > sudo tee md5sum.txt
        ''')
        os.chdir(workdir)
        log.info('$ finished extras build repository')

    def write_conf(self, source, destination, context):
        log = self.app.log
        log.info('^ started extras write conf')
        result = ''
        with open(source, 'r') as f:
            t = Template(f.read())
            result = t.render(context)
            f.close()
        with open(destination, 'w') as f:
            f.write(result)
            f.close()
        log.info('$ finished extras write conf')
