from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from settings import API_TOKEN

from django.core.wsgi import get_wsgi_application  # Need for use ORM
_django_app = get_wsgi_application()  # Need for use ORM

from botstate import machine


bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

engine = machine.Machine(bot, None)