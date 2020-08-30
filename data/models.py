import sys
from typing import List
from django.db import models
from aiogram import types
from botstate import states
from aioutils import sync_to_async


class User(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255, null=True)
    chat_id = models.IntegerField(null=True)
    state = models.CharField(max_length=255)
    substate = models.IntegerField(null=True)

    solving_mode = models.BooleanField(default=False)
    current_task = models.CharField(max_length=255, null=True)
    solved_task_list = models.CharField(max_length=512, default='')

    @classmethod
    @sync_to_async
    def create(cls, message: types.Message):
        user = cls(name=message.from_user.first_name,
                   chat_id=message.chat.id,
                   telegram_id=message.from_user.username,
                   state=states.State.GREETING.name)
        user.save()
        return user

    @staticmethod
    @sync_to_async
    def get_user_by_chat_id(chat_id: int):
        return User.objects.get(chat_id=chat_id)

    @sync_to_async
    def async_save(self):
        self.save()

    @staticmethod
    def add_solved_task(user: 'User', task_name: str) -> None:
        SEPARATOR: str = '#'
        task_list: List[str] = User.get_task_list(user)
        task_list.append(task_name)
        user.solved_task_list = SEPARATOR.join(task_list)
        user.save()

    @staticmethod
    def check_solve_task(user: 'User', task_name: str) -> bool:
        SEPARATOR: str = '#'
        task_list: List[str] = User.get_task_list(user)
        return True if task_name in task_list else False

    @staticmethod
    def get_not_done_tasks(user: 'User', all_tasks: List['FreeAnswerQuiz']) -> List[str]:
        SEPARATOR: str = '#'

        all_tasks_set = {task.name for task in all_tasks}

        task_list: List[str] = User.get_task_list(user)
        done_tasks = set(task_list)
        return list(all_tasks_set - done_tasks)

    @staticmethod
    def get_task_list(user: 'User') -> List[str]:
        SEPARATOR: str = '#'
        return user.solved_task_list.split(SEPARATOR)


class Message(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255)
    media_name = models.CharField(max_length=255, null=True)

    group = models.CharField(max_length=255, null=True)
    order = models.IntegerField(null=True)

    next_button_name = models.CharField(max_length=255, null=True)
    previous_button_name = models.CharField(max_length=255, null=True)

    @staticmethod
    @sync_to_async
    def get_message_by_name(name: str) -> 'Messages':
        return Message.objects.get(name=name)

    @staticmethod
    @sync_to_async
    def filter_message_by_group(group: str) -> 'Messages':
        return Message.objects.filter(group=group)


class LinkedMessages(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)

    group = models.CharField(max_length=255, null=True)

    next_state = models.CharField(max_length=255, null=True)

    @staticmethod
    @sync_to_async
    def get_linked_message_by_name(name: str) -> 'LinkedMessages':
        return LinkedMessages.objects.get(name=name)


class FreeAnswerQuiz(models.Model):

    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)
    question = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, related_name='question')

    right_answer = models.CharField(max_length=255)

    hint = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, related_name='hint')
    wrong_answer_action = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, related_name='wrong_answer_action')
    right_answer_action = models.ForeignKey(
        Message,  on_delete=models.SET_NULL, null=True, related_name='related_primary_manual_roats')

    next_quiz = models.ForeignKey(
        'FreeAnswerQuiz',  on_delete=models.SET_NULL, null=True, related_name='next_quiz_fk')

    @staticmethod
    @sync_to_async
    def get_quiz_by_name(name: str) -> 'FreeAnswerQuiz':
        return FreeAnswerQuiz.objects.get(name=name)

    @staticmethod
    @sync_to_async
    def get_quiz_all() -> List['FreeAnswerQuiz']:
        return FreeAnswerQuiz.objects.all()
