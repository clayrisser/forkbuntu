import os
import sys
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
    helpers.mkdir(settings['sourcedir'] + '/ubuntu=meta')

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
