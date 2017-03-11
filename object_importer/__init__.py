import os
import sys

from django.core.wsgi import get_wsgi_application


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
