from unittest2 import TestCase

from snake.dependencies import DependencyGraph, CircularDependencyException


class DependencyGraphTests(TestCase):
    def test_node_unknown_to_dependencies_resolves_to_itself(self):
        dependencies = DependencyGraph()

        self.assertEqual(['a'], dependencies.resolve('a'))

    def test_node_with_no_dependencies_resolves_to_itself(self):
        dependencies = DependencyGraph()
        dependencies.add('a', [])

        self.assertEqual(['a'], dependencies.resolve('a'))

    def test_it_resolves_simple_dependencies(self):
        dependencies = DependencyGraph()
        dependencies.add('a', ['c'])
        dependencies.add('a', ['b'])

        self.assertEqual(['c', 'b', 'a'], dependencies.resolve('a'))

    def test_it_resolves_complex_dependencies(self):
        dependencies = DependencyGraph()
        dependencies.add('a', ['b', 'c'])
        dependencies.add('b', ['c', 'e'])
        dependencies.add('c', ['e', 'd'])

        self.assertEqual(['e', 'd', 'c', 'b', 'a'], dependencies.resolve('a'))

    def test_it_detects_cycles_from_starting_node(self):
        dependencies = DependencyGraph()
        dependencies.add('a', ['b'])
        dependencies.add('b', ['a'])

        expected = "^Circular dependency detected: a => b => a$"
        with self.assertRaisesRegexp(CircularDependencyException, expected):
            dependencies.resolve('a')

    def test_it_detects_cycles_from_non_starting_node(self):
        dependencies = DependencyGraph()
        dependencies.add('a', ['b'])
        dependencies.add('b', ['c'])
        dependencies.add('c', ['d'])
        dependencies.add('d', ['b'])

        expected = "a => b => c => d => b"
        with self.assertRaisesRegexp(CircularDependencyException, expected):
            dependencies.resolve('a')
