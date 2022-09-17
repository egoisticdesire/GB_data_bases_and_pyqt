import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE, TIME, USER
from client import create_presence, process_server_message


class TestClient(unittest.TestCase):
    base_msg = {
            ACTION: PRESENCE,
            TIME: 111.111,
            USER: {
                    ACCOUNT_NAME: 'test_guest'
            }
    }
    server_msg_200 = {
            RESPONSE: 200
    }

    server_msg_400 = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
    }

    def test_presence_message_ok(self):
        test_presence_msg = create_presence('test_guest')
        test_presence_msg[TIME] = 111.111
        self.assertEqual(test_presence_msg, self.base_msg)

    def test_presence_message_err(self):
        test_presence_msg = create_presence('guest')
        self.assertNotEqual(test_presence_msg, self.base_msg)

    def test_process_server_message_200_ok(self):
        self.assertEqual(process_server_message(self.server_msg_200), '200: OK')

    def test_process_server_message_200_err(self):
        self.assertNotEqual(process_server_message(self.server_msg_200), '400: Bad Request')

    def test_process_server_message_400_ok(self):
        self.assertEqual(process_server_message(self.server_msg_400), '400: Bad Request')

    def test_process_server_message_400_err(self):
        self.assertNotEqual(process_server_message(self.server_msg_400), '200: OK')

    def test_process_server_message_exception_ok(self):
        self.assertRaises(ValueError, process_server_message, self.base_msg)


if __name__ == '__main__':
    unittest.main()
