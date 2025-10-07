"""
WSGI config for exam project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

path = '/home/mhykeborhlar/exam_app'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'exam.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
