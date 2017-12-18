from cfoundation import Service

class TaskService(Service):

    def started(self, task_name):
        log = self.app.log
        log.info('Started \'' + task_name + '\'')

    def finished(self, task_name):
        log = self.app.log
        log.info('Finished \'' + task_name + '\'')
