from subprocess import call


class ShellWrapper(object):
    def __init__(self, app):
        self.app = app

    def execute(self, command):
        self.app.info(command)
        exit_status = call(command, shell=True)
        if exit_status != 0:
            self.app.abort(exit_status)
