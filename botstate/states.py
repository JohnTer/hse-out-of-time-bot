from enum import Enum


class State(Enum):
    GREETING: int = 1
    WAITING: int = 2
    DASHBOARD: int = 3
    QUIZ: int = 4
