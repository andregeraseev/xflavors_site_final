"""
WSGI config for xflavors project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from xflavors import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xflavors.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(settings.BASE_DIR, 'media'), prefix='media/')

