from node import Node


class MigrationGraph(object):
    """Only retain what is applicable here..."""
    built = False

    def __init__(self, migrations):
        self.node_map = {}
        self.nodes = {}
        self.migrations = migrations

    def add_node(self, key, implementation):
        node = Node(key, implementation)
        self.node_map[key] = node
        self.nodes[key] = implementation

    def add_arcs(self, child, parent):
        """Establish 'parent' and 'child' relationships."""
        if not self.built:
            raise Exception('Must initialize graph before adding dependencies')

        if child not in self.node_map:
            raise ValueError('Non existent node for child: `%s`.' % child)

        if parent not in self.node_map:
            raise ValueError('Non existent node for parent: `%s`.' % parent)

        self.node_map[child].add_parent(self.node_map[parent])
        self.node_map[parent].add_child(self.node_map[child])

    def configure_arcs(self):
        """Configure parent and child arcs for applicable nodes."""
        for key, migration in self.migrations.iteritems():
            for constraint in migration.constraints:
                self.add_arcs(key, constraint)

    def build(self):
        """Build graph and mark as such."""
        for key, migration in self.migrations.iteritems():
            self.add_node(key, migration)

        self.built = True
        self.configure_arcs()

    def _maybe_merge_parent_node(self, node):
        # TODO: protect against StopIteration?
        next_parent = next(
            parent for parent in node.parents if not parent.merged
        )
        next_parent.previous = node.key
        self.maybe_merge_node(next_parent)

    def _maybe_merge_child_node(self, node):
        if not node.imported:  # will this really ever happen?
            self.importer.merge(node)
        else:
            raise ValueError('HOW DID WE GET HERE?')

        if all(child for child in node.children if child.merged):
            # all parents and all children merged, meaning all done here?
            # can I safely rely on all parents having been merged?
            return
        else:
            if node.previous:
                previous_node = self.node_map[node.previous]
                # go back to this guy instead of random child
                self.maybe_merge_node(previous_node)
            else:
                # go back to a child?
                next_child = next(
                    child for child in node.children if not child.merged
                )
                self.maybe_merge_node(next_child)

    def maybe_merge_node(self, node):
        if all(parent for parent in node.parents if parent.merged):
            self._maybe_merge_child_node(node)
        else:
            self._maybe_merge_parent_node(node)

    def run_migrations(self):
        """Migrate all root nodes.

        This is preferable to immediately traversing the tree
        as some objects might have more than one parent -
        all of which might be in the root_node list.

        Then, traverse graph in Depth First Search to import all nodes.
        """
        for node in self.root_nodes():
            self.importer.merge(node)  # or whatever

        for node in self.root_nodes():
            for child in node.children:
                self.maybe_merge_node(child)

    def root_nodes(self):
        """Return all root nodes."""
        roots = set()
        for node in self.nodes:
            if not node.parents:
                roots.add(node)

        return roots  # TODO: use as generator function?

    def _nodes_and_edges(self):
        nodes = len(self.node_map.keys())
        edges = sum(len(node.parents) for node in self.node_map.values())
        return nodes, edges

    def __str__(self):
        return 'Graph: %s nodes, %s edges' % self._nodes_and_edges()

    def __repr__(self):
        name = self.__class__.__name__
        nodes, edges = self._nodes_and_edges()
        return '<%s: nodes=%s, edges=%s>' % (name, nodes, edges)

    def __contains__(self, node):
        return node in self.nodes
