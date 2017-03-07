import os
import sys
from importlib import import_module

from django.core.wsgi import get_wsgi_application

from migration_graph import MigrationGraph


DATABASE_CONNECTION = 'foo'

project_path = '/Users/thomasweaver/projects/snapchat-ads-service'
# This is so Django knows where to find stuff.
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'snapchat_ads_service.settings'
)
sys.path.append(project_path)

# This is so local_settings.py gets loaded.
os.chdir(project_path)
# This is so models get loaded.
application = get_wsgi_application()

# this file will need to be scp copied to remote box
# DB to connect to should be added to settings here (remove when done?):


def load_migrations(migrations):
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

    import_target_template = 'migrations.%s'
    for migration_name in migration_names:
        import_target = import_target_template % migration_name
        migration_module = import_module(import_target)
        migrations[migration_name] = migration_module.Migration

migrations = {}
load_migrations(migrations)

# initialize graph
graph = MigrationGraph()
for key, migration in migrations.items():
    graph.add_node(key, migration)

graph.initialized = True

# build graph
for key, migration in migrations.iteritems():
    for constraint in migration.constraints:
        graph.add_dependency(key, constraint)

graph.run_migrations()
