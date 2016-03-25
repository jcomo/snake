from subprocess import call
from unittest import TestCase


class PEP8Tests(TestCase):
    CHECKED_DIRS = ['tests', 'snake']
    IGNORED_RULES = ['E501']

    def test_pep8(self):
        pep8_command = 'env pep8 %s %s' % (self._ignore_rules(), self._check_dirs())
        if call(pep8_command, shell=True):
            raise Exception("PEP8 Failed. Check stdout for more information")

    def _check_dirs(self):
        return ' '.join(self.CHECKED_DIRS)

    def _ignore_rules(self):
        return '--ignore=%s' % ','.join(self.IGNORED_RULES)
