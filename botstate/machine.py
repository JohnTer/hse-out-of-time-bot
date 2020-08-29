import asyncio
from typing import Optional, List

from .states import State

from data import models
from telegram import message
from aiogram import Bot, types


class GreetingState(object):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.previous_state: Optional[State] = None
        self.next_state: Optional[State] = State.DASHBOARD.name

        self.linked_message_name = 'greeting'
        self.context: Optional[message.MessageContext] = None

    async def _get_linked_message(self, name: str) -> models.LinkedMessages:
        return await models.LinkedMessages.get_linked_message_by_name(name)

    async def set_context(self):
        linked_message: models.LinkedMessages = await self._get_linked_message(
            self.linked_message_name)
        self.context = message.MessageContext(self.bot, linked_message)
        await self.context.init_context()

    async def _next_state_handler(self, user: models.User):
        user.state = self.next_state
        user.substate = None
        await user.async_save()

    async def incoming_handler(self, user: models.User, payload_data: int, message_id: int) -> Optional[bool]:
        next_state_flag: Optional[bool] = await self.context.run_incoming(
            user, payload_data, message_id)

        if next_state_flag is None:
            return
        elif next_state_flag == True:
            await self._next_state_handler(user)
        elif next_state_flag == False:
            pass
        else:
            raise Exception()
        return next_state_flag

    async def outcoming_handler(self, user: models.User) -> None:
        return await self.context.run_oucoming(user)

    async def handler(self, user: models.User, payload_data: Optional[int] = None, message_id: Optional[int] = None, outcoming_flag: bool = False) -> Optional[bool]:
        if outcoming_flag:
            return await self.outcoming_handler(user)
        else:
            return await self.incoming_handler(user, payload_data, message_id)


class DashboardState(object):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.previous_state: Optional[State] = None
        self.next_state: Optional[str] = State.QUIZ.name
        self.default_state: Optional[str] = State.DASHBOARD.name
        self.finish_state: Optional[str] = State.WAITING.name

        self.outcoming_message = 'welcome_menu'
        self.finish_message = 'finish'

        self._prepare_context()

    def _prepare_context(self):
        self.context: message.DashboardContext = message.DashboardContext(
            self.bot)

    async def _next_state_handler(self, user: models.User, task: str):
        user.state = self.next_state
        user.substate = None
        user.solving_mode = False
        user.current_task = task
        await user.async_save()

    async def _finish_state_handler(self, user: models.User):
        user.state = self.finish_state
        user.substate = None
        user.solving_mode = False
        user.current_task = None
        await user.async_save()

    async def incoming_handler(self, user: models.User, text: str, message_id: int):
        result: Optional[str] = await self.context.run_incoming(user, text, message_id)
        if result is not None:
            await self._next_state_handler(user, result)

    async def outcoming_handler(self, user: models.User, not_done_tasks: Optional[List[str]] = None):
        message: str = self.outcoming_message
        if not_done_tasks is None:
            not_done_tasks: List[str] = await self._get_not_done_tasks(user)

        if len(not_done_tasks) == 0:
            await self._finish_state_handler(user)
            message = self.finish_message
        await self.context.run_outcoming(user, message, not_done_tasks)

    def _check_corectness(self, text: str, not_done_tasks: List[str]) -> str:
        return True if text in not_done_tasks else False

    async def _get_not_done_tasks(self, user: models.User) -> List[str]:
        all_tasks: List[models.FreeAnswerQuiz] = await models.FreeAnswerQuiz.get_quiz_all()
        return models.User.get_not_done_tasks(user, all_tasks)

    async def handler(self, user: models.User, text: str, message_id: int, init: bool = False):
        not_done_tasks: List[str] = await self._get_not_done_tasks(user)
        if init or not self._check_corectness(text, not_done_tasks):
            await self.outcoming_handler(user, not_done_tasks)
        else:
            await self.incoming_handler(user, text, message_id)


class QuizState(object):
    def __init__(self, bot: Bot, user: models.User) -> None:
        self.bot = bot

        self.previous_state: Optional[State] = State.DASHBOARD.name

        self.task_name = user.current_task

        self.context: Optional[message.QuizContext] = None

    async def _get_quiz(self, name: str) -> models.FreeAnswerQuiz:
        return await models.FreeAnswerQuiz.get_quiz_by_name(name)

    async def set_context(self) -> None:
        quiz: models.FreeAnswerQuiz = await self._get_quiz(self.task_name)
        self.context = message.QuizContext(self.bot, quiz)

    async def _back_to_menu(self, user: models.User) -> None:
        user.state = self.previous_state
        user.solving_mode = False
        user.current_task = None
        await user.async_save()

    async def run_oucoming(self, user: models.User):
        await self.context.run_oucoming(user, 'question')
        user.solving_mode = True
        await user.async_save()
        return None

    async def right_answer_handler(self, user: models.User):
        solved_task: str = user.current_task
        models.User.add_solved_task(user, solved_task)
        await self._back_to_menu(user)

    async def run_incoming(self, user: models.User, test: str):
        text_type: str = await self.context.run_incoming(user, test)
        if text_type == 'back':
            await self._back_to_menu(user)
            return True
        elif text_type == 'right_answer':
            await self.right_answer_handler(user)
            return True
        return None

    async def handler(self, user: models.User, text: str):
        if not user.solving_mode:
            return await self.run_oucoming(user)
        else:
            return await self.run_incoming(user, text)


class WaitingState(object):
    def __init__(self, bot: Bot, user: models.User) -> None:
        self.bot = bot

        self._prepare_context()

    def _prepare_context(self):
        self.context = message.WaitingContext(self.bot)

    async def handler(self, user: models.User, text: str, message_id: Optional[int]):
        await self.context.run_incoming(user, text, message_id)


class Machine(object):
    def __init__(self, bot: Bot, loop: asyncio.AbstractEventLoop) -> None:
        self.bot: Bot = bot
        self.event_loop: asyncio.AbstractEventLoop = loop

    async def _create_new_user(self, tg_message: types.Message) -> None:
        user: models.User = await models.User.create(tg_message)
        return user

    async def _get_user_by_message(self, tg_message: types.Message) -> Optional[models.User]:
        chat_id: int = tg_message.chat.id
        user_object: models.User = None
        try:
            user_object = await models.User.get_user_by_chat_id(chat_id)
        except models.User.DoesNotExist:
            user_object = await self._create_new_user(tg_message)
        return user_object

    def _change_count_loop(self, count_loop: int, next_state: Optional[bool]) -> int:
        if next_state is None:
            return count_loop
        else:
            return count_loop + 1

    async def message_handler(self, tg_message: types.Message) -> None:
        loop_count_iterations: int = 1

        user: models.User = await self._get_user_by_message(tg_message)

        i: int = 0
        while i < loop_count_iterations:
            next_state:  Optional[bool] = None
            if user.state == State.GREETING.name:
                sthandl = GreetingState(self.bot)
                await sthandl.set_context()
                next_state = await sthandl.handler(user, outcoming_flag=True)
            if user.state == State.DASHBOARD.name:
                sthandl = DashboardState(self.bot)
                await sthandl.handler(user, tg_message.text, tg_message.message_id, bool(i))
            if user.state == State.QUIZ.name:
                sthandl = QuizState(self.bot, user)
                await sthandl.set_context()
                next_state = await sthandl.handler(user, tg_message.text)
            if user.state == State.WAITING.name:
                sthandl = WaitingState(self.bot, user)
                next_state = await sthandl.handler(user, tg_message.text, message_id=tg_message.message_id)

            i += 1
            loop_count_iterations = self._change_count_loop(
                loop_count_iterations, next_state)

    async def callback_handler(self, callback_query: types.CallbackQuery):
        user: models.User = await self._get_user_by_message(callback_query.message)

        if user.state == State.GREETING.name:
            sthandl = GreetingState(self.bot)
            await sthandl.set_context()
            await sthandl.handler(user, int(callback_query.data), callback_query.message.message_id)
        if user.state == State.DASHBOARD.name:
            sthandl = DashboardState(self.bot)
            await sthandl.outcoming_handler(user)
