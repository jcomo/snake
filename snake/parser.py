from optparse import OptionParser


class ApplicationArgsParser(object):
    @classmethod
    def parse(cls, tokens):
        parser = OptionParser()
        parser.add_option('-T', '--tasks', dest='show_tasks', action='store_true',
                          help="Display the tasks with descriptions and exits")
        parser.add_option('-t', '--trace', dest='trace', action='store_true',
                          help="Turn on verbose backtraces")
        parser.add_option('-f', '--snakefile', dest='filename', metavar='FILE',
                          help="Use FILE as the Snakefile")

        opts, remaining = parser.parse_args(tokens)
        tasks, args = cls()._parse_positional_args(remaining)

        return tasks, args, opts

    def __init__(self):
        self._tasks = []
        self._args = {}

    def _parse_positional_args(self, tokens):
        for token in tokens:
            if '=' in token:
                self._parse_arg(token)
            else:
                self._parse_task(token)

        return self._tasks, self._args

    def _parse_task(self, token):
        self._tasks.append(token)

    def _parse_arg(self, token):
        """
        Arguments come from the command line in the form of key=value
        """
        key, value = token.split('=')
        self._args[key] = value
