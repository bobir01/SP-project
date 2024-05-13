import logging
import re
import socket
import ssl
from typing import Dict
import json


# here we are creating socket client for making HTTP request
class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # set up SSL context and wrap it
        self.sslContext = ssl_sock = ssl.create_default_context()
        self.socket = self.sslContext.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                                  server_hostname=self.host)

    # preparing HTTP request. This function returns encoded request as byte
    def prepare_request(self, body: Dict, path) -> bytes:
        path = path
        body_json = json.dumps(body)
        headers = f'POST {path} HTTP/1.1\r\nHost: {self.host}\r\nContent-Type: application/json\r\nAccept: application/json\r\nContent-Length: {len(body_json)}\r\n\r\n'
        request = headers.encode() + body_json.encode()
        return request

    def send_request(self, request):
        server_address = (self.host, self.port)
        self.socket.connect(server_address)
        # here we check whether socket is connected or not to avoid ambiguity
        try:
            self.socket.sendall(request)
            data = self.receive_response()
            logging.info("Received data: %s" % data.decode())
            pattern = r'HTTP\/\d+\.\d+ (\d+)'
            json_match = re.search(pattern, data.decode())

            if json_match:
                status_code = int(json_match.group(0).split(' ')[1])

                if status_code == 200:
                    return {'ok': True, 'description': 'Success', 'data': json.loads(data.decode().split('\r\n\r\n')[1])}
                elif status_code == 400:
                    return {'ok': False, 'description': 'Chat not found', 'data': json.loads(data.decode().split('\r\n\r\n')[1])}
            else:
                raise json.JSONDecodeError("No JSON data found in response", data.decode(), 0)


        except socket.error as e:
            return {'ok': False, 'description': 'Socket error', 'data': str(e)}

        except json.JSONDecodeError as e:
            return {'ok': False, 'description': 'JSON decode error', 'data': 'None'}
        finally:
            self.close()

    # recieves the HTTP respose from the server
    def receive_response(self, buffer_size=4096):
        return self.socket.recv(buffer_size)

    # closes socket connection
    def close(self):
        self.socket.close()


class TelegramSocketClient(SocketClient):
    def __init__(self, bot_token, chat_id):
        host = 'api.telegram.org'
        port = 443
        super().__init__(host, port)
        self.path = f"/bot{bot_token}/sendMessage"
        self.bot_token = bot_token
        self.chat_id = chat_id

    # prepare request for specifically Telegram API
    def prepare_telegram_request(self, body):
        return self.prepare_request(body, self.path)

    # in order to send message first we construct the message body after,
    # prepare the request and send it using base class method 'send_request'
    def send_telegram_message(self, message: str):
        body = {
            'chat_id': self.chat_id,
            'text': message
        }
        request = self.prepare_telegram_request(body)
        return self.send_request(request)


if __name__ == '__main__':
    # Usage
    # token = "7155087790:AAEQIRoSeZ6CsXDb-ltJXCJHe44_ZBAKDZA"
    # id = "881939669"  # muzaffar's ID
    # telegram_client = TelegramSocketClient(token, id)
    # telegram_client.send_telegram_message("Hello")
    pass
