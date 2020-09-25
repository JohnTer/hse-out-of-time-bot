import time
import logging

from aiogram import types

from settings import MESSAGE_TIMEOUT

def timeout_message_middleware(message: types.Message) -> bool:
    current_time: float = time.time()
    if abs(message.date.timestamp() - current_time) > MESSAGE_TIMEOUT:
        logging.warning('the message \"%s\" by user %d was discarded by timeout (send time %d)',
                        message.text, message.from_user.id, message.date.timestamp())
        return False
    return True