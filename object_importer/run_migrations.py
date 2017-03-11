import os
from importlib import import_module

from migration_graph import MigrationGraph


def _load_migrations():
    migration_names = set()
    migration_directory = os.path.dirname(
        os.path.realpath(__file__)
    ) + '/migrations'

    for name in os.listdir(migration_directory):
        if not name.endswith('.py'):
            continue

        import_name = name.rsplit('.', 1)[0]
        # skip 'private' files
        if import_name[0] not in '_':
            migration_names.add(import_name)

    migrations = {}
    import_target_template = 'migrations.%s'
    for migration_name in migration_names:
        import_target = import_target_template % migration_name
        migration_module = import_module(import_target)
        migrations[migration_name] = migration_module.Migration

    return migrations


def run_migrations():
    """Use Directed Graph of migrations to import data."""
    migrations = _load_migrations()
    graph = MigrationGraph(migrations)
    graph.build()
    graph.run_migrations()


if __name__ == '__main__':
    run_migrations()
