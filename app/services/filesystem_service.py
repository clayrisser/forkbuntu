import os
from cfoundation import Service

class FilesystemService(Service):
    def update_filesystem_size(self, workdir):
        log = self.app.log
        log.info('^ started update filesystem size')
        contents_path = workdir + '/contents'
        filesystem_path = workdir + '/filesystem'
        os.chdir(filesystem_path)
        os.popen('du -sx --block-size=1 ./ | cut -f1 | sudo tee ' + contents_path + '/install/filesystem.size').read()
        os.chdir(workdir)
        log.info('$ finished update filesystem size')
