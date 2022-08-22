"""
It is a launcher for starting subprocesses for server and clients of two types: senders and listeners.
for more information:
https://stackoverflow.com/questions/67348716/kill-process-do-not-kill-the-subprocess-and-do-not-close-a-terminal-window
"""

import os
import signal
import subprocess
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CLIENTS_COUNT = 2


def get_subprocess(file_with_args):
    sleep(0.5)
    file_full_path = f'{PYTHON_PATH} {BASE_PATH}/{file_with_args}'
    args = ['gnome-terminal', '--disable-factory', '--', 'bash', '-c', file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


process = []
while True:
    TEXT_FOR_INPUT = f'Запустить сервер и клиенты - (r); ' \
                     f'Закрыть клиенты - (x); ' \
                     f'Выйти - (q): '
    USER_ANSWER = input(TEXT_FOR_INPUT)

    if USER_ANSWER == 'q':
        break
    elif USER_ANSWER == 'r':
        process.append(get_subprocess('server.py'))
        for i in range(CLIENTS_COUNT):
            process.append(get_subprocess(f'client.py -n t{i + 1}'))

    elif USER_ANSWER == 'x':
        while process:
            victim = process.pop()
            os.killpg(victim.pid, signal.SIGINT)
