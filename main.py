# Django specific settings
import os
import time
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
application = get_wsgi_application()


import concurrent.futures
import asyncio
from botstate import machine

from telegram.message import MessageContext, QuizContext
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher.webhook import SendMessage
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, types
import logging

from data import models



loop = asyncio.get_event_loop()

from local_settings import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

engine = machine.Machine(bot, loop)


@dp.message_handler()
async def echo(message: types.Message):
    current_time = time.time()
    if abs(message.date.timestamp() - current_time) > 10:
        return
    await engine.message_handler(message)
    return


@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    current_time = time.time()
    if False and abs(callback_query.message.date.timestamp() - current_time) > 10:
        return
    await engine.callback_handler(callback_query)
    return


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def clean_handler(message: types.Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def on_startup(dp):
    with open('webhook_cert.pem', 'rb') as f:
        await bot.set_webhook(WEBHOOK_URL, certificate=f.read())
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        loop=loop
    )
