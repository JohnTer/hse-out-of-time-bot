import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = (
    'data',
)

SECRET_KEY = '1234567s'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOG_FORMAT = '%(name)s - %(levelname)s - %(asctime)s # %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%I:%M:%S')

from local_settings import *
