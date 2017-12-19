import os
from getpass import getuser
from cfoundation import Service

class FilesystemService(Service):

    def update_filesystem_size(self, workdir):
        s = self.app.services
        s.task_service.started('update_filesystem_size')
        contents_path = workdir + '/contents'
        filesystem_path = workdir + '/filesystem'
        os.chdir(filesystem_path)
        filesystem_size = os.popen('du -sx --block-size=1 ./').read().split('\t')[0]
        os.popen('echo ' + filesystem_size + ' | sudo tee ' + contents_path + '/install/filesystem.size').read()
        os.popen('sudo chown ' + getuser() + ':' + getuser() + ' ' + contents_path + '/install/filesystem.size')
        os.chdir(workdir)
        s.task_service.finished('update_filesystem_size')
