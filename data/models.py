import sys
from typing import List
from django.db import models
from aiogram import types
from botstate import states


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
    def create(cls, message: types.Message):
        return cls(name=message.from_user.first_name,
                   chat_id=message.chat.id,
                   telegram_id=message.from_user.username,
                   state=states.State.GREETING.name)

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
    path_media_content = models.CharField(max_length=255, null=True)

    group = models.CharField(max_length=255, null=True)
    order = models.IntegerField(null=True)

    next_button_name = models.CharField(max_length=255, null=True)
    previous_button_name = models.CharField(max_length=255, null=True)


class LinkedMessages(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255)

    group = models.CharField(max_length=255, null=True)

    next_state = models.CharField(max_length=255, null=True)


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
