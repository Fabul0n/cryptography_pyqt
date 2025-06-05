from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import websockets
import requests
from sympy import randprime


class WebSocketClient(QObject):
    message_received = pyqtSignal(str)
    key_received = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)
    connect_request_received = pyqtSignal(str, str, str)

    def __init__(self, username, chat_window, loop):
        super().__init__()
        self.username = username
        self.chat_window = chat_window
        self.websocket = None
        self.loop = loop
        self.A = None
        self.p = None
        self.g = None
        self.r = None
        self.a = None

    async def fetch_params(self):
        try:
            response = requests.get("http://127.0.0.1:8000/get_params")
            response.raise_for_status()
            params = response.json()
            self.p = int(params["p"])
            self.g = int(params["g"])
            self.r = int(params["r"])
            self.chat_window.p = self.p
            self.chat_window.g = self.g
            print(f"{self.username} получил параметры: p={self.p}, g={self.g}, r={self.r}")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка получения параметров: {e}")
            raise

    def generate_keys(self):
        self.a = randprime(2**2047, 2**2048) ^ self.r
        self.chat_window.a = self.a
        self.A = pow(self.g, self.a, self.p)
        print(f"{self.username} сгенерировал ключи: a={self.a}, A={self.A}")

    async def send_hello(self):
        if self.websocket:
            await self.websocket.send(f"__HELLO__:{self.username}")

    async def connect_and_listen(self):
        uri = "ws://127.0.0.1:8000/ws"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                await self.fetch_params()
                self.generate_keys()
                await self.send_hello()
                while True:
                    msg = await websocket.recv()
                    print(f"{self.username} получил сообщение: {msg}")
                    if msg.startswith("__HELLO__:"):
                        try:
                            _, name = msg.split(":", 1)
                            self.key_received.emit(name, 0)
                        except ValueError as e:
                            self.error_occurred.emit(f"Некорректный формат HELLO: {e}")
                    elif msg.startswith("__CONNECT_REQUEST__:"):
                        try:
                            _, from_user, to_user, public_key = msg.split(":", 3)
                            print(f"{self.username} получил публичный ключ от {from_user}: {public_key}")
                            self.connect_request_received.emit(from_user, to_user, public_key)
                        except ValueError as e:
                            self.error_occurred.emit(f"Некорректный формат запроса на подключение: {e}")
                    elif msg.startswith("__CONNECT_RESPONSE__:"):
                        try:
                            _, from_user, to_user, response, public_key = msg.split(":", 4)
                            print(f"{self.username} получил публичный ключ от {from_user}: {public_key}")
                            self.message_received.emit(f"__CONNECT_RESPONSE__:{from_user}:{to_user}:{response}:{public_key}")
                        except ValueError as e:
                            self.error_occurred.emit(f"Некорректный формат ответа на подключение: {e}")
                    else:
                        self.message_received.emit(msg)
        except Exception as e:
            self.error_occurred.emit(f"Ошибка подключения: {e}")

    async def _send_message_coroutine(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def send_message(self, message):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._send_message_coroutine(message), self.loop)

    def get_public_key(self):
        return self.A