import os
import logging

from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS = (
    'data',
)

LOG_FORMAT = '%(name)s - %(levelname)s - %(asctime)s # %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%I:%M:%S')


load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

API_TOKEN = os.getenv('API_TOKEN')

# webhook settings
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_PORT = os.getenv('WEBHOOK_PORT')

# webserver settings
WEBAPP_HOST = os.getenv('WEBAPP_HOST')
WEBAPP_PORT = os.getenv('WEBAPP_PORT')

# django secret key
SECRET_KEY = os.getenv('SECRET_KEY')

WEBHOOK_URL = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

MESSAGE_TIMEOUT = 10 # sec
