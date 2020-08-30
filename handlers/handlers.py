import time
import logging

from aiogram import types

from loader import dp, bot, engine

@dp.message_handler()
async def echo(message: types.Message):
    current_time = time.time()
    if abs(message.date.timestamp() - current_time) > 10:
        logging.warning('the message \"%s\" by user %d was discarded by timeout (send time %d)',
                        message.text, message.from_user.id, message.date.timestamp())
        return
    await engine.message_handler(message)
    logging.info('the message \"%s\" by user %d was processed in %f ms', message.text, message.from_user.id, (time.time() - current_time)*1000)
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