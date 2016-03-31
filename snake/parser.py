from optparse import OptionParser

flags_parser = OptionParser()
flags_parser.add_option('-f', '--snakefile', dest='filename', metavar='FILE',
                        help="Use FILE as the Snakefile")
flags_parser.add_option('-t', '--trace', dest='trace', action='store_true',
                        help="Turn on verbose backtraces")
flags_parser.add_option('-T', '--tasks', dest='show_tasks', action='store_true',
                        help="Display the tasks with descriptions and exit")
flags_parser.add_option('--version', dest='version', action='store_true',
                        help="Display the version information and exit")


class ApplicationArgsParser(object):
    """Parses the arguments used in the command line. Snake uses a combination
    of option flags, positional, and keyword arguments. In order to properly
    parse the arguments, a combination of OptionParser and custom parsing is
    used. The option parser eats up all of the program options and the rest
    is left as positional arguments to be parsed as task names and keyword
    arguments for tasks.
    """
    @classmethod
    def parse(cls, tokens):
        """
        Parses the command line and returns the list of tasks to execute, the
        keyword arguments to use, and the program arguments passed in.

        :return: tuple of tasks, keyword arguments, and program options
        """
        opts, remaining = flags_parser.parse_args(tokens)
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
