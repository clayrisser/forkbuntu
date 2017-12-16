import os
from os import path
from distutils.dir_util import copy_tree
from jinja2 import Template

def copy(extras, workdir, app):
    contentspath = path.join(workdir, 'contents')
    os.popen('sudo mkdir -p ' + contentspath + '/pool/extras').read()
    copy_tree(extras, path.join(contentspath, 'pool', 'extras'))
    app.log.info('Copied extras')

def build_repository(workdir, name, dist, app):
    indicespath = path.join(workdir, 'indices')
    ftparchivepath = path.join(workdir, 'apt-ftparchive')
    contentspath = path.join(workdir, 'contents')
    ftparchivessourcepath = path.abspath(path.join(path.dirname(path.realpath(__file__)), '..', 'apt-ftparchive'))
    if not path.exists(indicespath):
        os.mkdir(indicespath)
    os.chdir(indicespath)
    suffixes = [
        'extra.main',
        'main',
        'main.debian-installer',
        'restricted',
        'restricted.debian-installer'
    ]
    for suffix in suffixes:
        os.popen('wget http://archive.ubuntu.com/ubuntu/indices/override.' + dist + '.' + suffix)
    if not path.exists(ftparchivepath):
        os.mkdir(ftparchivepath)
    context = {
        'workdir': workdir,
        'dist': dist
    }
    write_conf(
        source=path.join(ftparchivessourcepath, 'apt-ftparchive-dev.conf'),
        destination=path.join(ftparchivepath, 'apt-ftparchive-dev.conf'),
        context=context
    )
    write_conf(
        source=path.join(ftparchivessourcepath, 'apt-ftparchive-extras.conf'),
        destination=path.join(ftparchivepath, 'apt-ftparchive-extras.conf'),
        context=context
    )
    write_conf(
        source=path.join(ftparchivessourcepath, 'apt-ftparchive-udeb.conf'),
        destination=path.join(ftparchivepath, 'apt-ftparchive-udeb.conf'),
        context=context
    )
    write_conf(
        source=path.join(ftparchivessourcepath, 'release.conf'),
        destination=path.join(ftparchivepath, 'release.conf'),
        context=context
    )
    os.chdir(contentspath)
    os.system('''
    apt-ftparchive packages pool/extras > dists/stable/extras/binary-amd64/Packages
    gzip -c dists/stable/extras/binary-amd64/Packages | tee dists/stable/extras/binary-amd64/Packages.gz > /dev/null
    apt-ftparchive -c ''' + ftparchivepath + '''/release.conf generate ''' + ftparchivepath + '''/apt-ftparchive-deb.conf
    apt-ftparchive -c ''' + ftparchivepath + '''/release.conf generate ''' + ftparchivepath + '''/apt-ftparchive-udeb.conf
    apt-ftparchive -c ''' + ftparchivepath + '''/release.conf generate ''' + ftparchivepath + '''/apt-ftparchive-extras.conf
    apt-ftparchive -c ''' + ftparchivepath + '''/release.conf release ''' + contentspath + '''/dists/''' + dist + ''' > ''' + contentspath + '''/dists/''' + dist + '''/Release
    gpg --default-key "''' + name + '''" --output ''' + contentspath + '''/dists/''' + dist + '''/Release.gpg -ba ''' + contentspath + '''/dists/''' + dist + '''/Release
    find \. -type f -print0 | xargs -0 md5sum > sudo tee md5sum.txt
    ''')
    os.chdir(workdir)
    app.log.info('Built repository')

def write_conf(source, destination, context):
    result = ''
    with open(source, 'r') as f:
        t = Template(f.read())
        result = t.render(context)
        f.close()
    with open(destination, 'w') as f:
        f.write(result)
        f.close()
