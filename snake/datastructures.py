from collections import MutableMapping


class LenientDict(MutableMapping):
    """A class describing a dict that does not raise when using bracket notation on a key that
    does not exist. Implements the core dict interface.
    """
    def __init__(self, dct=None):
        self._dict = dct or {}

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        try:
            return self._dict[key]
        except KeyError:
            pass

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        try:
            del self._dict[key]
        except KeyError:
            pass
