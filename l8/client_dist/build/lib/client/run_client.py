import argparse
import os.path
import sys

from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

sys.path.append('../')
from client.main_window import ClientMainWindow
from client.start_dialog import UsernameDialog
from client.transport import ClientTransport
from db.client_db_config import ClientDB
from logs.client_log_config import LOGGER
from common.errors import ServerError
from common.decorators import Log
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT


@Log
def args_parser():
    """
    Command line argument parser, returns a tuple of 4 elements: server address, port, username, password.
    Performs validation of the port number.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_addr = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_pswd = namespace.password

    # Проверяем порт
    if not 1023 < server_port < 65536:
        LOGGER.error(f'Порт {server_port} недопустим. Возможны варианты от 1024 до 65535.')
        exit(1)

    return server_addr, server_port, client_name, client_pswd


def main():
    """Main function."""

    global transport

    # Загружаем параметы коммандной строки
    server_addr, server_port, client_name, client_pswd = args_parser()
    # Создаём клиентское приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке, то запросим его
    start_dialog = UsernameDialog()
    if not client_name or not client_pswd:
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект.
        # Иначе - выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_pswd = start_dialog.client_pswd.text()
            LOGGER.debug(f'Username: {client_name}; Password: {client_pswd}')
        else:
            exit(0)

    LOGGER.info(f'Клиент запущен с параметрами: {server_addr}:{server_port}; имя пользователя: {client_name}')

    # Если не существует директории "keys" - создаем
    if not os.path.exists('keys'):
        os.mkdir('keys')

    # Загружаем ключи с файла и если файла нет, то генерируем новую пару.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'keys/{client_name}.key')

    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    database = ClientDB(client_name)

    try:
        transport = ClientTransport(
            server_port,
            server_addr,
            database,
            client_name,
            client_pswd,
            keys
        )
    except ServerError as err:
        message = QMessageBox()
        message.critical(start_dialog, 'Server error', err.text)
        exit(1)

    transport.daemon = True
    transport.start()

    del start_dialog

    # Создаём GUI
    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Telegram на минималках :: {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()
