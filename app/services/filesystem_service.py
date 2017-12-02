import os

def update_filesystem_size(basedir):
    print('Updating filesystem size . . .')
    os.chdir(basedir + '/filesystem')
    os.system('du -sx --block-size=1 ./ | cut -f1 > ' + basedir + '/FinalCD/install/filesystem.size')
    os.chdir(basedir)
