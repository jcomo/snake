from unittest2 import TestCase

from snake.datastructures import LenientDict


class LenientDictTestCase(TestCase):

    def test_it_modifies_the_underlying_dict(self):
        base = {'a': 1}

        d = LenientDict(base)
        d['a'] = 2

        self.assertEqual(2, d['a'])
        self.assertEqual(2, base['a'])

    def test_it_acts_like_dict(self):
        d = LenientDict({'a': 1})
        d['b'] = 2

        self.assertEqual(2, len(d))
        self.assertEqual(1, d['a'])
        self.assertEqual(2, d['b'])
        self.assertTrue('a' in d)
        self.assertFalse('c' in d)

        for key in d:
            pass

    def test_it_returns_nothing_instead_of_raising_for_key_error(self):
        d = LenientDict()

        self.assertIsNone(d['a'])

    def test_it_deletes_without_raising_key_error(self):
        d = LenientDict()

        del d['a']
