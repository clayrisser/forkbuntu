import os
from os import path

def burn(workdir, app):
    contentspath = path.join(workdir, 'contents')
    os.chdir(contentspath)
    os.system('''
    xorriso -as mkisofs -r -V "Custom Ubuntu Install CD" \
    -cache-inodes \
    -J -l -b isolinux/isolinux.bin \
    -c isolinux/boot.cat -no-emul-boot \
    -boot-load-size 4 -boot-info-table \
    -o ''' + workdir + '''/custom.iso ''' + contentspath + '''
    ''')
    os.chdir(workdir)
    app.log.info('All built')
