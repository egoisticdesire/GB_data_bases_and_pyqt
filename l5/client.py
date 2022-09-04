import argparse
import sys

from PyQt5.QtWidgets import QApplication

sys.path.append('../')
from client.main_window import ClientMainWindow
from client.start_dialog import UsernameDialog
from client.transport import ClientTransport
from common.errors import ServerError
from db.client_db_config import ClientDB
from logs.client_log_config import LOGGER
from common.decorators import Log
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT


@Log
def args_parser():
    """
    Парсим аргументы командной строки.
    Читаем параметры, возвращаем 3 параметра.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_addr = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверяем порт
    if not 1023 < server_port < 65536:
        LOGGER.error(f'Порт {server_port} недопустим. Возможны варианты от 1024 до 65535.')
        exit(1)

    return server_addr, server_port, client_name


def main():
    global transport

    # Загружаем параметы коммандной строки
    server_addr, server_port, client_name = args_parser()
    # Создаём клиентокое приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке, то запросим его
    if not client_name:
        start_dialog = UsernameDialog()
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект.
        # Иначе - выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    LOGGER.info(f'Клиент запущен с параметрами: {server_addr}:{server_port}; имя пользователя: {client_name}')

    database = ClientDB(client_name)

    try:
        transport = ClientTransport(server_addr, server_port, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)

    transport.daemon = True
    transport.start()

    # Создаём GUI
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Telegram на минималках :: {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()
