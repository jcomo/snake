from unittest2 import TestCase

from snake.datastructures import LenientDict


class LenientDictTestCase(TestCase):
    def test_it_acts_like_dict(self):
        d = LenientDict({'a': 1})
        d['b'] = 2

        self.assertEqual(1, d['a'])
        self.assertEqual(2, d['b'])
        self.assertTrue('a' in d)
        self.assertFalse('c' in d)

    def test_it_returns_nothing_instead_of_raising_for_key_error(self):
        d = LenientDict()

        self.assertIsNone(d['a'])
