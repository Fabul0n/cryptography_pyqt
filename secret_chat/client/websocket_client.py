from PyQt6.QtCore import QObject, pyqtSignal
import asyncio
import websockets
import requests
from sympy import randprime, primitive_root


class WebSocketClient(QObject):
    message_received = pyqtSignal(str)
    key_received = pyqtSignal(str, tuple)
    error_occurred = pyqtSignal(str)
    connect_request_received = pyqtSignal(str, str)  # from_user, to_user

    def __init__(self, username, chat_window, loop):
        super().__init__()
        self.username = username
        self.chat_window = chat_window
        self.websocket = None
        self.loop = loop

    async def fetch_params(self):
        try:
            response = requests.get("http://localhost:8000/get_params")
            response.raise_for_status()
            params = response.json()
            self.p = int(params["p"])
            self.g = int(params["g"])
            self.r = int(params["r"])
            self.chat_window.p = self.p
        except Exception as e:
            self.error_occurred.emit(f"Ошибка получения параметров: {e}")
            raise

    def generate_keys(self):
        self.a = randprime(2**2047, 2**2048)
        self.chat_window.a = self.a
        masked_a = self.a ^ self.r
        self.A = pow(self.g, masked_a, self.p)

    async def send_public_key(self):
        if self.websocket:
            await self.websocket.send(f"__HELLO__:{self.username}:{self.A}")

    async def connect_and_listen(self):
        uri = "ws://localhost:8000/ws"
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                await self.fetch_params()
                self.generate_keys()
                await self.send_public_key()
                while True:
                    msg = await websocket.recv()
                    if msg.startswith("__HELLO__:"):
                        try:
                            _, name, e_str = msg.split(":", 3)
                            other_public_key = (int(e_str), 0)
                            self.key_received.emit(name, other_public_key)
                        except ValueError as e:
                            self.error_occurred.emit(f"Некорректный формат ключа: {e}")
                    elif msg.startswith("__CONNECT_REQUEST__:"):
                        try:
                            _, from_user, to_user = msg.split(":", 3)
                            self.connect_request_received.emit(from_user, to_user)
                        except ValueError as e:
                            self.error_occurred.emit(f"Некорректный формат запроса на подключение: {e}")
                    elif msg.startswith("__CONNECT_RESPONSE__:"):
                        try:
                            _, from_user, to_user, response = msg.split(":", 4)
                            self.message_received.emit(f"__CONNECT_RESPONSE__:{from_user}:{response}")
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