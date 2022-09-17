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


def get_subprocess(file_with_args):
    PYTHON_PATH = sys.executable
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    sleep(1)
    file_full_path = f'{PYTHON_PATH} {BASE_PATH}/{file_with_args}'
    args = ['gnome-terminal', '--disable-factory', '--', 'bash', '-c', file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


process = []
while True:
    TEXT_FOR_INPUT = 'Запустить сервер - (s); ' \
                     'Запустить клиенты - (с); ' \
                     'Закрыть клиенты - (x); ' \
                     'Выйти - (q): '
    USER_ANSWER = input(TEXT_FOR_INPUT)

    if USER_ANSWER == 'q':
        break
    elif USER_ANSWER == 's':
        process.append(get_subprocess('server.py'))
    elif USER_ANSWER == 'c':
        clients_count = int(input('Количество тест-клиентов: '))
        for i in range(clients_count):
            process.append(get_subprocess(f'client.py -n test{i + 1} -p qwerty123'))
    elif USER_ANSWER == 'x':
        while process:
            victim = process.pop()
            os.killpg(victim.pid, signal.SIGINT)
