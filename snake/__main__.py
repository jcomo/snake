import sys

from .snake import _instance


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    _instance.run()
