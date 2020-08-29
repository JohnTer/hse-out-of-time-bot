from typing import List, Optional, Dict

from aiogram import Bot, types

from data import models

from .keyboard import SimpleKeyboard, QuizKeyboard, DashboardKeyboard
from botstate import states


class MessageContext(object):
    def __init__(self, bot: Bot, linked_message: models.LinkedMessages) -> None:
        self.bot: Bot = bot
        self.linked_message: models.LinkedMessages = linked_message
        self.user: Optional[models.User] = None

        self.message_list: Optional[List[models.Message]] = None

    async def init_context(self):
        message_group: str = self.linked_message.group
        self.message_list = list(
            await models.Message.filter_message_by_group(message_group))
        self.message_list.sort(key=lambda x: x.order)

    def _get_user_current_substate(self, user: models.User) -> str:
        if user.substate == None:
            user.substate = 0
        return user.substate

    def _get_message(self, substate: int) -> Optional[models.Message]:
        if substate >= len(self.message_list):
            return None
        return self.message_list[substate]

    async def _send_message(self, user: models.User, message: models.Message, message_id: Optional[int]) -> None:
        chat_id: int = user.chat_id
        text: str = message.text_content
        keyboard: types.InlineKeyboardMarkup = SimpleKeyboard.get_markup(
            message)
        if message_id is None:
            await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
        else:
            await self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

    async def _clear_keyboard(self, user: models.User, message_id: int):
        chat_id: int = user.chat_id
        await self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)

    async def run_oucoming(self, user: models.User, message_id: Optional[int] = None) -> Optional[bool]:
        user_substate: int = self._get_user_current_substate(user)
        message: models.Message = self._get_message(user_substate)
        if message is not None:
            await self._send_message(user, message, message_id)
            await user.async_save()
        else:
            await self._clear_keyboard(user, message_id)
            return True
        return None

    async def run_incoming(self, user: models.User, payload_data: int, message_id: int) -> Optional[bool]:
        if payload_data == 1:
            user.substate += 1
        elif payload_data == 0:
            user.substate -= 1
        else:
            raise Exception()
        return await self.run_oucoming(user, message_id)


class QuizContext(object):
    def __init__(self, bot: Bot, primary_quiz: models.FreeAnswerQuiz) -> None:
        self.bot: Bot = bot
        self.primary_quiz: models.FreeAnswerQuiz = primary_quiz
        self.current_quiz: models.FreeAnswerQuiz = self.primary_quiz
        self.user: Optional[models.User] = None

        self.menu_state = None

    async def _send_message(self, user: models.User, message: models.Message) -> None:
        chat_id: int = user.chat_id
        text: str = message.text_content
        keyboard: types.InlineKeyboardMarkup = QuizKeyboard.get_markup(
            self.current_quiz)
        await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

    def _get_question(self, quiz: models.FreeAnswerQuiz) -> models.Message:
        return quiz.question

    def _get_hint(self, quiz: models.FreeAnswerQuiz) -> models.Message:
        return quiz.hint

    def _get_right_answer(self, quiz: models.FreeAnswerQuiz) -> models.Message:
        return quiz.right_answer_action

    def _get_wrong_answer(self, quiz: models.FreeAnswerQuiz) -> models.Message:
        return quiz.wrong_answer_action

    async def run_oucoming(self, user: models.User, text_type: str) -> str:
        if text_type == 'question':
            message: models.Message = self._get_question(self.current_quiz)
        elif text_type == 'hint':
            message: models.Message = self._get_hint(self.current_quiz)
        elif text_type == 'right_answer':
            message: models.Message = self._get_right_answer(self.current_quiz)
        elif text_type == 'wrong_answer':
            message: models.Message = self._get_wrong_answer(self.current_quiz)
        elif text_type == 'back':
            return text_type
        else:
            Exception()

        await self._send_message(user, message)
        return text_type

    def _check_right_answer(self, text: str) -> bool:
        right_answer: str = self.current_quiz.right_answer
        text = text.strip().lower()
        right_answer = right_answer.strip().lower()
        return True if text == right_answer else False

    async def run_incoming(self, user: models.User, text: str, firts_time: bool = False):
        text_type: Optional[str] = None

        if firts_time:
            text_type = 'question'
        elif text == QuizKeyboard.hint_text:
            text_type = 'hint'
        elif text == QuizKeyboard.menu_text:
            text_type = 'back'
        elif self._check_right_answer(text):
            text_type = 'right_answer'
        else:
            text_type = 'wrong_answer'
        return await self.run_oucoming(user, text_type)


class DashboardContext(object):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.user: Optional[models.User] = None

    def _format_text(self, text: str) -> str:
        return text.strip()

    def _check_correctness_text(self, text: str) -> bool:
        return self._format_text(text).isnumeric()

    async def _incorrect_text_handler(self, user: models.User, message_id: int) -> None:
        await self.bot.send_message(chat_id=user.chat_id, text='Dashboard trash')
        # await self.bot.delete_message(chat_id=user.chat_id, message_id=message_id)

    async def run_incoming(self, user: models.User, text: str, message_id: int) -> Optional[str]:
        if not self._check_correctness_text(text):
            await self._incorrect_text_handler(user, message_id)
            return None
        else:
            return self._format_text(text)

    async def _get_message(self, name: str) -> models.Message:
        return await models.Message.get_message_by_name(name)

    async def _send_message(self, user: models.User, message: models.Message, not_done_tasks: List[str]) -> None:
        chat_id: int = user.chat_id
        text: str = message.text_content
        keyboard: types.ReplyKeyboardMarkup = DashboardKeyboard.get_markup(
            not_done_tasks)
        await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

    async def run_outcoming(self, user: models.User, message_name: str, not_done_tasks: List[str]):
        message: models.Message = await self._get_message(message_name)
        await self._send_message(user, message, not_done_tasks)


class WaitingContext(object):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    async def _incorrect_text_handler(self, user: models.User, message_id: int) -> None:
        await self.bot.delete_message(chat_id=user.chat_id, message_id=message_id)

    async def run_incoming(self, user: models.User, text: str, message_id: int):
        await self._incorrect_text_handler(user, message_id)
