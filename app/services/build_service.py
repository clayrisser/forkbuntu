import os
from os import path

def build_repository(basedir):
    if not path.exists(basedir + '/apt-ftparchive'):
        os.mkdir(basedir + '/apt-ftparchive')
    os.system('''
    mkdir -p /opt/indices /opt/apt-ftparchive
    cd /opt/indices/
    DIST=xenial
    for SUFFIX in extra.main main main.debian-installer restricted restricted.debian-installer; do
    wget http://archive.ubuntu.com/ubuntu/indices/override.$DIST.$SUFFIX
    done
    ''')
