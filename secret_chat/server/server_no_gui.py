from PyQt6.QtCore import QThread, pyqtSignal
from fastapi import FastAPI, WebSocket
from uvicorn import Config, Server
from sympy import randprime, isprime, primitive_root
import asyncio


class WebSocketServer(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.connections = {}  # {websocket: username}
        self.init_params()

    def init_params(self):
        """Инициализация параметров Диффи-Хеллмана."""
        while True:
            q = randprime(10**29, 10**30)
            self.p = 2 * q + 1
            if isprime(self.p):
                self.g = primitive_root(self.p)
                self.a = randprime(2**2047, 2**2048)
                break

    async def get_params(self):
        """Возвращает параметры Диффи-Хеллмана для клиентов."""
        return {"p": str(self.p), "g": str(self.g), "r": str(self.a)}

    async def websocket_endpoint(self, ws: WebSocket):
        """Обрабатывает WebSocket-соединения и сообщения."""
        await ws.accept()
        self.message_received.emit("🔌 Клиент подключён")

        if len(self.connections) >= 2:
            self.message_received.emit("⚠️ Сервер заполнен, клиент отклонён")
            await ws.send_text("Сервер заполнен.")
            await ws.close(code=4000)
            return

        username = None
        try:
            data = await ws.receive_text()
            if data.startswith("__HELLO__:"):
                _, username, key = data.split(":", 2)
                self.connections[ws] = username
                self.message_received.emit(f"👤 Пользователь {username} подключён")
                for conn in self.connections:
                    if conn != ws:
                        await conn.send_text(f"__HELLO__:{username}:{key}")
            else:
                self.message_received.emit(f"⚠️ Ожидалось __HELLO__, получено: {data}")
                await ws.close(code=4001)
                return

            while True:
                data = await ws.receive_text()
                self.message_received.emit(f"📥 Получено от {username}: {data}")
                
                if data.startswith("__CONNECT_REQUEST__:"):
                    try:
                        _, from_user, to_user = data.split(":", 3)
                        for conn, name in self.connections.items():
                            if name == to_user and conn != ws:
                                await conn.send_text(f"__CONNECT_REQUEST__:{from_user}:{to_user}")
                                self.message_received.emit(f"📤 Запрос на подключение от {from_user} к {to_user}")
                                break
                        else:
                            self.message_received.emit(f"⚠️ Пользователь {to_user} не найден")
                            await ws.send_text(f"__CONNECT_RESPONSE__:{to_user}:{from_user}:REJECT")
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат запроса на подключение: {data}")
                        continue
                
                elif data.startswith("__CONNECT_RESPONSE__:"):
                    try:
                        _, from_user, to_user, response = data.split(":", 4)
                        for conn, name in self.connections.items():
                            if name == to_user and conn != ws:
                                await conn.send_text(f"__CONNECT_RESPONSE__:{from_user}:{to_user}:{response}")
                                self.message_received.emit(f"📤 Ответ на подключение от {from_user} к {to_user}: {response}")
                                break
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат ответа на подключение: {data}")
                        continue
                
                elif data.startswith("__TO__:"):
                    try:
                        _, target_name, message = data.split(":", 2)
                        for conn, name in self.connections.items():
                            if name == target_name and conn != ws:
                                await conn.send_text(f"{username}: {message}")
                                self.message_received.emit(f"📤 Сообщение от {username} к {target_name}: {message}")
                                break
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат сообщения: {data}")
                        continue
                
                else:
                    for conn in self.connections:
                        if conn != ws:
                            await conn.send_text(f"{username}: {data}")
                            self.message_received.emit(f"📤 Сообщение от {username} всем: {data}")

        except Exception as e:
            if username:
                self.message_received.emit(f"🔌 Пользователь {username} отключён: {str(e)}")
            else:
                self.message_received.emit(f"🔌 Клиент отключён: {str(e)}")
            self.connections.pop(ws, None)

    def run(self):
        """Запуск FastAPI-сервера в отдельном событийном цикле."""
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/get_params")(self.get_params)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        config = Config(app=self.app, host="127.0.0.1", port=8000, loop=loop)
        server = Server(config=config)
        loop.run_until_complete(server.serve())