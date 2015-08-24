# sample mod_wsgi conf file
import os
import sys
path = '/var/www/joie/joieAPI'
if path not in sys.path:
    sys.path.insert(0, '/var/www/joie/joieAPI')
os.environ['DJANGO_SETTINGS_MODULE'] = 'joieAPI.settings'
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()