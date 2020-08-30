import logging
from settings import WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL

from aiogram.utils.executor import start_webhook
from aiogram import types

from loader import bot, dp

async def on_startup(dp):
    logging.info('Starting bot...')
    await bot.set_webhook(WEBHOOK_URL, certificate=types.InputFile('webhook_cert.pem'))
    logging.info('Certificate was uploaded successfully.')


async def on_shutdown(dp):
    logging.info('Shutting down...')
    logging.info('Delete webhook...')
    await bot.delete_webhook()
    logging.info('Webhook was deleted.')
    logging.warning('The bot was disabled.')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
