class CommandLineParser(object):
    @classmethod
    def parse(cls, tokens):
        return cls().parse_command(tokens)

    def __init__(self):
        self._tasks = []
        self._args = {}
        self._flags = {}

    def parse_command(self, tokens):
        for token in tokens:
            if token.startswith('-'):
                self._parse_flag(token)
            elif '=' in token:
                self._parse_arg(token)
            else:
                self._parse_task(token)

        return self._tasks, self._args, self._flags

    def _parse_task(self, token):
        self._tasks.append(token)

    def _parse_arg(self, token):
        """
        Arguments come from the command line in the form of key=value
        """
        key, value = token.split('=')
        self._args[key] = value

    def _parse_flag(self, token):
        """
        Flags can be passed as --flag=value, --flag, or -f. In the case that
        flags are passed in without a value, their respective value in the
        returned dict will be True
        """
        flag = token.lstrip('-')

        try:
            key, value = flag.split('=')
        except ValueError:
            key, value = flag, True

        self._flags[key] = value
