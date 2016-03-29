class CircularDependencyException(Exception):
    def __init__(self, cycle):
        message = 'Circular dependency detected: %s' % ' => '.join(cycle)
        super(CircularDependencyException, self).__init__(message)


class DependencyGraph(object):
    def __init__(self):
        self._vertices = {}

    def add_dependency(self, node, on=frozenset()):
        self._initialize_node(node)

        for dependency in on:
            self._add_dependency(node, dependency)

    def _initialize_node(self, node):
        if node not in self._vertices:
            self._vertices[node] = []

    def _add_dependency(self, node, dependency):
        self._initialize_node(dependency)
        self._vertices[node].append(dependency)

    def resolve(self, start):
        return self._resolve_node(start, [], [])

    def _resolve_node(self, node, resolved, unresolved):
        unresolved.append(node)

        for dependency in self._vertices[node]:
            if dependency in resolved:
                continue

            if dependency in unresolved:
                raise CircularDependencyException(unresolved + [dependency])

            self._resolve_node(dependency, resolved, unresolved)

        unresolved.remove(node)
        resolved.append(node)

        # We can just return at the end since steps in the recursion are
        # getting references to the resolved list and modifying it "globally"
        return resolved
