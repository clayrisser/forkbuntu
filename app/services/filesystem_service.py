import os

def update_filesystem_size(workdir, app):
    contentspath = workdir + '/contents'
    filesystempath = workdir + '/filesystem'
    os.chdir(filesystempath)
    os.popen('du -sx --block-size=1 ./ | cut -f1 | sudo tee ' + contentspath + '/install/filesystem.size').read()
    os.chdir(workdir)
    app.log.info('Filesystem size updated')
