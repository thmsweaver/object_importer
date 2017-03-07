class Node(object):
    """
    A single node in the migration graph.
    Contains direct links to adjacent nodes in either direction.
    """
    imported = False

    def __init__(self, key, implementation):
        self.key = key
        self.implementation = implementation
        self.children = set()
        self.parents = set()
        self.previous = None

    def __eq__(self, other):
        return self.key == other

    def __lt__(self, other):
        return self.key < other

    def __hash__(self):
        return hash(self.key)

    def __getitem__(self, item):
        return self.key[item]

    def __str__(self):
        return str(self.key)

    def __repr__(self):
        return '<Node: (%s)>' % self.key

    def add_child(self, child):
        self.children.add(child)

    def add_parent(self, parent):
        self.parents.add(parent)

    def mark_as_imported(self):
        self.imported = True
