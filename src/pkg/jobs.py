import os
import sys
import re
from pkg import helpers

def mkdirs(settings):
    helpers.mkdir(settings['basedir'])
    helpers.mkdir(settings['basedir'] + '/FinalCD')
    helpers.mkdir(settings['cdsourcedir'])
    helpers.mkdir(settings['extrasdir'])
    helpers.mkdir(settings['extrasdir'] + '/preseed')
    helpers.mkdir(settings['extrasdir'] + '/pool/extras')
    helpers.mkdir(settings['sourcedir'])
    helpers.mkdir(settings['sourcedir'] + '/keyring')
    helpers.mkdir(settings['sourcedir'] + '/indices')
    helpers.mkdir(settings['sourcedir'] + '/ubuntu-meta')

def keyring(settings):
    response = os.system('gpg --list-keys | grep "'+ settings['gpgkeyname'] + '" >/dev/null')
    if response != 0:
        print('No GPG Key found in your keyring.')
        print('Generating a new gpg key (' + settings['gpgkeyname'] + ' ' + settings['gpgkeycomment'] + ') with a passphrase of ' + settings['gpgkeyphrase'] + ' . . .')
        with open(settings['basedir'] + '/key.inc', 'w') as f:
            f.write('''Key-Type: DSA
Key-Length: 1024
Subkey-Type: ELG-E
Subkey-Length: 2048
Name-Real: ''' + settings['gpgkeyname'] + '''
Name-Comment: ''' + settings['gpgkeycomment'] + '''
Name-Email: ''' + settings['gpgkeyemail'] + '''
Expire-Date: 0
Passphrase: ''' + settings['gpgkeyphrase'] + '''\n''')
        os.system('gpg --gen-key --batch --gen-key ' + settings['basedir'] + '/key.inc')

def mountiso(settings):
    if not os.path.isfile(settings['cdsourcedir'] + '/md5sum.txt'):
        print('Mounting Ubuntu iso . . .')
        response = os.system('mount | grep ' + settings['cdsourcedir'])
        if response == 0:
            os.system('umount ' + settings['cdsourcedir'])

        os.system('mount -o loop ' + settings['basedir'] + '/' + settings['cdimage'] + ' ' + settings['cdsourcedir'] + '/')
        if not os.path.isfile(settings['cdsourcedir'] + '/md5sum.txt'):
            print('Mount did not succeed')
            sys.exit(1)
        else:
            print('Mount successful')

def ftparchive(settings):
    if not os.path.isfile(settings['sourcedir'] + '/apt.conf'):
        print('No APT.CONF file found... generating one.')
        os.system('cat ' + settings['cdsourcedir'] + '/dists/breezy/Release | egrep -v "^ " | egrep -v "^(Date|MD5Sum|SHA1)" | sed \'s/: / "/\' | sed \'s/^/APT::FTPArchive::Release::/\' | sed \'s/$/";/\' > ' + settings['sourcedir'] + '/apt.conf')
    if not os.path.isfile(settings['sourcedir'] + '/apt-ftparchive-deb.conf'):
        with open(settings['sourcedir'] + '/apt-ftparchive-deb.conf', 'w') as f:
            f.write('''Dir {
  ArchiveDir "''' + settings['basedir'] + '''/FinalCD";
};

TreeDefault {
  Directory "pool/";
};

BinDirectory "pool/main" {
  Packages "dists/breezy/main/binary-i386/Packages";
  BinOverride "''' + settings['sourcedir'] + '''/indices/override.breezy.main";
  ExtraOverride "''' + settings['sourcedir'] + '''/indices/override.breezy.extra2.main";
};

Default {
  Packages {
    Extensions ".deb";
    Compress ". gzip";
  };
};

Contents {
  Compress "gzip";
};"
''')
    if not os.path.isfile(settings['sourcedir'] + '/apt-ftparchive-udeb.conf'):
        with open(settings['sourcedir'] + '/apt-ftparchive-udev.conf', 'w') as f:
            f.write('''Dir {
  ArchiveDir "''' + settings['basedir'] + '''/FinalCD";
};

TreeDefault {
  Directory "pool/";
};

BinDirectory "pool/main" {
  Packages "dists/breezy/main/debian-installer/binary-i386/Packages";
  BinOverride "''' + settings['sourcedir'] + '''/indices/override.breezy.main.debian-installer";
};

Default {
  Packages {
    Extensions ".udeb";
    Compress ". gzip";
  };
};

Contents {
  Compress "gzip";
};"
''')
    if not os.path.isfile(settings['sourcedir'] + '/apt-ftparchive-extras.conf'):
        with open(settings['sourcedir'] + '/apt-ftparchive-extras.conf', 'w') as f:
            f.write('''Dir {
  ArchiveDir "''' + settings['basedir'] + '''/FinalCD";
};

TreeDefault {
  Directory "pool/";
};

BinDirectory "pool/extras" {
  Packages "dists/breezy/extras/binary-i386/Packages";
};

Default {
  Packages {
    Extensions ".deb";
    Compress ". gzip";
  };
};

Contents {
  Compress "gzip";
};"
''')
    if not os.path.isfile(settings['sourcedir'] + '/indices/override.breezy.extra.main'):
        for i in [
            'override.breezy.extra.main',
            'override.breezy.main',
            'override.breezy.main.debian-installer'
        ]:
            os.system('cd ' + settings['sourcedir'] + '/indices && wget http://archive.ubuntu.com/ubuntu/indices/' + i)
    os.system('cat ' + settings['sourcedir'] + '/indices/override.breezy.extra.main | egrep -v \' Task \' > ' + settings['sourcedir'] + '/indices/override.breezy.extra2.main')
    os.system('cat ' + settings['cdsourcedir'] + '/dists/breezy/main/binary-i386/Packages | perl -e \'while (<>) { chomp; if(/^Package\:\s*(.+)$/) { $pkg=$1; } elsif(/^Task\:\s(.+)$/) { print "$pkg\tTask\t$1\n"; } }\' >> ' + settings['sourcedir'] + '/indices/override.breezy.extra2.main')

def resync(settings):
    print('Re-syncing old data . . .')
    os.system('''
    cd ''' + settings['basedir'] + '''/FinalCD
    rsync -atz --delete ''' + settings['cdsourcedir'] + '/ ' + settings['basedir'] + '''/FinalCD/
    ''')

def remove_packages(settings):
    if not os.path.isfile(settings['packagelist']):
        print('No PackageList found. Assuming that you do not require any packages to be removed')
    else:
        os.system('cat ' + settings['packagelist'] + ' | grep "^ii" | awk \'{print $2 "_" $3}\' > ' + settings['sourcedir'] + '/temppackages')
        print('Removing files that are no longer required . . .')
        filenames = os.popen('cd ' + settings['basedir'] + '/FinalCD && find pool/main -type f -name "*.deb" -print').read().split('\n')
        filenames = filenames[:len(filenames) - 1]
        to_remove = []
        for i in filenames:
            match = re.findall(r'(?<=\/)[a-zA-Z0-9\.\-\_\+]+(?=_.+\.deb)', i)[0]
            with open(settings['sourcedir'] + '/temppackages') as f:
                for line in f.readlines():
                    if line.find(match) > -1:
                        to_remove.append(line)
        if len(to_remove) > 0:
            for remove in to_remove:
                pass
        else:
            print('Nothing to remove')

def keyfile(settings):
    print('Generating keyfile . . .')
    keyring = os.popen('find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print').read()
    if len(keyring) <= 0:
        print(2)
        keyring = os.popen('''
        # cd ''' + settings['sourcedir'] + '''/keyring
        apt-get source ubuntu-keyring &> /dev/null
        # find * -maxdepth 1 -name "ubuntu-keyring*" -type d -print
        ''').read()
        if len(keyring) <= 0:
            print(3)
            sys.exit('Cannot grab keyring source')
