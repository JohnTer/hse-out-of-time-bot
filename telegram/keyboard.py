from typing import List, Union, Tuple, Optional
from aiogram import Bot, Dispatcher, executor, types

from data import models


class SimpleKeyboard(object):
    @staticmethod
    def get_markup(message: models.Message) -> types.InlineKeyboardMarkup:
        keyboard_markup: types.InlineKeyboardMarkup = types.InlineKeyboardMarkup(
            row_width=3)

        text_and_data: List[Tuple[Union[str, int]]] = []

        if message.previous_button_name is not None:
            text_and_data.append((message.previous_button_name, 0))

        if message.next_button_name is not None:
            text_and_data.append((message.next_button_name, 1))

        row_btns: Tuple[types.InlineKeyboardButton] = (types.InlineKeyboardButton(text, callback_data=data)
                                                       for text, data in text_and_data)

        keyboard_markup.row(*row_btns)
        return keyboard_markup


class QuizKeyboard(object):
    hint_text: str = "Подсказка"
    menu_text: str = "В меню"

    @staticmethod
    def get_markup(quiz: models.FreeAnswerQuiz) -> types.ReplyKeyboardMarkup:
        keyboard: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
            resize_keyboard=True)
        if quiz.hint is not None:
            keyboard.add(types.KeyboardButton(text=QuizKeyboard.hint_text))
        keyboard.add(types.KeyboardButton(text=QuizKeyboard.menu_text))
        return keyboard


class DashboardKeyboard(object):
    COLUMN_NUM_SEPARATOR: int = 3

    @staticmethod
    def get_markup(tasks_name: List[str]) -> Union[types.ReplyKeyboardMarkup, types.ReplyKeyboardRemove]:
        if len(tasks_name) == 0:
            return types.ReplyKeyboardRemove()
        keyboard: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
            resize_keyboard=True)

        buttons: List[types.KeyboardButton] = []

        for i in range(1, len(tasks_name) + 1):
            buttons.append(types.KeyboardButton(tasks_name[i-1]))
            if i % DashboardKeyboard.COLUMN_NUM_SEPARATOR == 0 or i == len(tasks_name):
                keyboard.add(*buttons)
                buttons = []

        return keyboard
