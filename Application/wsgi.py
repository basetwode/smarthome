"""
WSGI config for Smart project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys


sys.path.append('/opt/smart/')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Application.settings")

application = get_wsgi_application()
# smart_home = _thread.start_new_thread(start_smarthome, ())

from Sensors.setup import setup as setup_sensors
from Actors.setup import setup as setup_actors
from SmartHome.controller import setup as setup_controller

setup_actors()
setup_sensors()
setup_controller()

# def handler_stop_signals(signum, frame):
#     GPIO.cleanup()
#
#
# signal.signal(signal.SIGINT, handler_stop_signals)
# signal.signal(signal.SIGTERM, handler_stop_signals)

# from IPCDriver.setup import setup
#
# setup()
