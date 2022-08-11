import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import ACCOUNT_NAME, ACTION, ENCODING, ERROR, PRESENCE, RESPONSE, TIME, USER
from common.utils import get_message, send_message


class TestSocket:
    """
    Тестирует отправку и получение сообщения, требует словарь.
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.received_msg = None

    def send(self, msg):
        """
        Отправляет сообщение, кодирует сообщение.
        :param msg:
        :return:
        """
        # Словарь -> строка
        json_test_msg = json.dumps(self.test_dict)
        # Строка -> байты
        self.encoded_msg = json_test_msg.encode(ENCODING)
        self.received_msg = msg

    def recv(self, max_len):
        """
        Получает данные из сокета.
        :return:
        """
        json_test_msg = json.dumps(self.test_dict)
        return json_test_msg.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_dict_send = {
            ACTION: PRESENCE,
            TIME: 111.111,
            USER: {
                    ACCOUNT_NAME: 'test_guest'
            }
    }
    test_dict_recv_ok = {
            RESPONSE: 200
    }
    test_dict_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
    }

    def test_send_ok(self):
        test_sock = TestSocket(self.test_dict_send)
        send_message(test_sock, self.test_dict_send)
        self.assertEqual(test_sock.encoded_msg, test_sock.received_msg)

    def test_send_err(self):
        test_sock = TestSocket(self.test_dict_send)
        send_message(test_sock, self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_sock, 'Is not a dictionary')

    def test_get_ok(self):
        test_sock = TestSocket(self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock), self.test_dict_recv_ok)

    def test_get_err(self):
        test_sock = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
