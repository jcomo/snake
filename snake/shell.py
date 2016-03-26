from subprocess import call


class CommandFailedException(Exception):
    def __init__(self, status, command):
        message = self._failure_message(status, command)
        super(CommandFailedException, self).__init__(message)

    def _failure_message(self, status, command):
        program = command.split(' ')[0]
        return "Command failed with status (%d): [%s...]" % (status, program)


class ShellWrapper(object):
    def __init__(self, logger):
        self.logger = logger

    def execute(self, command):
        self.logger.info(command)
        exit_status = call(command, shell=True)
        if exit_status != 0:
            raise CommandFailedException(exit_status, command)
