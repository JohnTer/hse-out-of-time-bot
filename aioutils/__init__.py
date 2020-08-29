from concurrent.futures import ThreadPoolExecutor

from .wrapper import *

MAX_WORKERS = 1
executor  = ThreadPoolExecutor(max_workers=MAX_WORKERS)