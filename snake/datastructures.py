class LenientDict(dict):
    """A class describing a dict that does not raise when using bracket notation on a key that
    does not exist. Behaves the same as a regular dict otherwise.
    """
    def __getitem__(self, key):
        try:
            return super(LenientDict, self).__getitem__(key)
        except KeyError:
            pass
