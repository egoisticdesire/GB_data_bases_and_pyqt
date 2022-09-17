import sys
import os
import json

sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from .decorators import Log
from .variables import ENCODING, MAX_PACKAGE_LENGTH


@Log
def get_message(client):
    """
    The function of receiving messages from remote computers.
    Receives JSON messages, decodes the received message,
    and checks that a dictionary has received.
    :param client: socket for data transfer.
    :return: dictionary - message.
    """

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@Log
def send_message(sock, message):
    """
    The function for sending dictionaries via a socket.
    Encodes a dictionary into JSON format and sends it over a socket.
    :param sock: socket to send
    :param message: dictionary to send
    :return: returns nothing.
    """

    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
