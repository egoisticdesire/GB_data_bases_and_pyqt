import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE, TIME, USER
from server import process_client_message


class TestServer(unittest.TestCase):
    server_msg_200 = {
            RESPONSE: 200
    }

    server_msg_400 = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
    }

    def test_process_client_message_ok(self):
        test_data = process_client_message({
                ACTION: PRESENCE,
                TIME: 111.111,
                USER: {
                        ACCOUNT_NAME: 'test_guest'
                }
        })
        self.assertEqual(test_data, self.server_msg_200)

    def test_process_client_message_err(self):
        test_data = process_client_message({
                ACTION: PRESENCE,
                TIME: 111.111,
                USER: {
                        ACCOUNT_NAME: 'test_guest'
                }
        })
        self.assertNotEqual(test_data, self.server_msg_400)

    def test_no_action(self):
        test_data = process_client_message({
                TIME: 111.111,
                USER: {
                        ACCOUNT_NAME: 'test_guest'
                }
        })
        self.assertEqual(test_data, self.server_msg_400)

    def test_no_time(self):
        test_data = process_client_message({
                ACTION: PRESENCE,
                USER: {
                        ACCOUNT_NAME: 'test_guest'
                }
        })
        self.assertEqual(test_data, self.server_msg_400)

    def test_data_is_dict(self):
        test_data_dict = process_client_message({
                ACTION: PRESENCE,
                TIME: 111.111,
                USER: {
                        ACCOUNT_NAME: 'test_guest'
                }
        })
        self.assertIsInstance(test_data_dict, dict)

    def test_data_is_not_dict(self):
        test_data_str = 'This is a string, not a dictionary'
        self.assertNotIsInstance(test_data_str, dict)


if __name__ == '__main__':
    unittest.main()
