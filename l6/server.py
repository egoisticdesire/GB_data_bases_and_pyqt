import argparse
import configparser
import os.path
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from db.server_db_config import ServerDB
from server.core import MessageProcessor

from common.decorators import Log
from common.variables import DEFAULT_PORT
from server.main_window import MainWindow


@Log
def args_parser(default_port, default_addr):
    """
    Парсим аргументы командной строки.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_addr, nargs='?')
    parser.add_argument('--no-gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_addr = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    return listen_addr, listen_port, gui_flag


@Log
def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server/server.ini')

    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Addr', '')
        config.set('SETTINGS', 'Database_path', 'db')
        config.set('SETTINGS', 'Database_file', 'server_db.db3')
        return config


@Log
def main():
    config = config_load()

    listen_addr, listen_port, gui_flag = args_parser(
        config['SETTINGS']['Default_port'],
        config['SETTINGS']['Listen_addr']
    )
    db = ServerDB(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']
        )
    )

    server = MessageProcessor(listen_addr, listen_port, db)
    server.daemon = True
    server.start()

    if gui_flag:
        while True:
            command = input('Type "exit" to shut down the server: ').lower()
            if command == 'exit':
                server.running = False
                server.join()
                break

    else:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(db, server, config)

        server_app.exec_()
        server.running = False


if __name__ == '__main__':
    main()
