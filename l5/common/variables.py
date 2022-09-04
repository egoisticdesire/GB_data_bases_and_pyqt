import logging
import sys

# DEFAULT CONFIG:
DEFAULT_IP_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 7777
MAX_CONNECTIONS = 5
CONNECTION_TIMEOUT = 0.5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
LOGGING_LVL = logging.DEBUG
DEFAULT_LOG_NAME = 'server' if 'server.py' in sys.argv[0] else 'client'
SERVER_CONFIG = 'server.ini'

# GUI CONFIG
WIDTH = 800
HEIGHT = 595

# JIM (JSON Instant Messaging) MAIN KEYS:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# JIM OTHER KEYS:
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

# SERVER RESPONSES:
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
