from unittest2 import TestCase

from snake.dependencies import DependencyGraph, CircularDependencyException


class DependencyGraphTests(TestCase):
    def test_node_with_no_dependencies_resolves_to_itself(self):
        graph = DependencyGraph()
        graph.add_dependency('a')

        self.assertEqual(['a'], graph.resolve('a'))

    def test_it_resolves_simple_dependencies(self):
        graph = DependencyGraph()
        graph.add_dependency('a')
        graph.add_dependency('a', ['c'])
        graph.add_dependency('a', ['b'])

        self.assertEqual(['c', 'b', 'a'], graph.resolve('a'))

    def test_it_resolves_complex_dependencies(self):
        graph = DependencyGraph()
        graph.add_dependency('a', ['b', 'c'])
        graph.add_dependency('b', ['c', 'e'])
        graph.add_dependency('c', ['e', 'd'])
        graph.add_dependency('d')
        graph.add_dependency('e')

        self.assertEqual(['e', 'd', 'c', 'b', 'a'], graph.resolve('a'))

    def test_it_detects_cycles_from_starting_node(self):
        graph = DependencyGraph()
        graph.add_dependency('a', ['b'])
        graph.add_dependency('b', ['a'])

        expected = "^Circular dependency detected: a => b => a$"
        with self.assertRaisesRegexp(CircularDependencyException, expected):
            graph.resolve('a')

    def test_it_detects_cycles_from_non_starting_node(self):
        graph = DependencyGraph()
        graph.add_dependency('a', ['b'])
        graph.add_dependency('b', ['c'])
        graph.add_dependency('c', ['d'])
        graph.add_dependency('d', ['b'])

        expected = "a => b => c => d => b"
        with self.assertRaisesRegexp(CircularDependencyException, expected):
            graph.resolve('a')
