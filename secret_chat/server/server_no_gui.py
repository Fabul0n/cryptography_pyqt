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
        self.connections = {}
        self.init_params()

    def init_params(self):
        while True:
            q = randprime(10**29, 10**30)
            self.p = 2 * q + 1
            if isprime(self.p):
                self.g = primitive_root(self.p)
                self.r = randprime(2**2047, 2**2048)  # Переименовано из a в r
                break
        print(f"Сервер инициализировал параметры: p={self.p}, g={self.g}, r={self.r}")

    async def get_params(self):
        return {"p": str(self.p), "g": str(self.g), "r": str(self.r)}

    async def websocket_endpoint(self, ws: WebSocket):
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
                _, username = data.split(":", 1)
                self.connections[ws] = username
                self.message_received.emit(f"👤 Пользователь {username} подключён")
            else:
                self.message_received.emit(f"⚠️ Ожидалось __HELLO__, получено: {data}")
                await ws.close(code=4001)
                return

            while True:
                data = await ws.receive_text()
                self.message_received.emit(f"📥 Получено от {username}: {data}")

                if data.startswith("__CONNECT_REQUEST__:"):
                    try:
                        _, from_user, to_user, public_key = data.split(":", 3)
                        for conn, name in self.connections.items():
                            if name == to_user and conn != ws:
                                await conn.send_text(f"__CONNECT_REQUEST__:{from_user}:{to_user}:{public_key}")
                                self.message_received.emit(f"📤 Запрос на подключение от {from_user} к {to_user} с ключом {public_key}")
                                break
                        else:
                            self.message_received.emit(f"⚠️ Пользователь {to_user} не найден")
                            await ws.send_text(f"__CONNECT_RESPONSE__:{to_user}:{from_user}:REJECT:0")
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат запроса на подключение: {data}")
                        continue

                elif data.startswith("__CONNECT_RESPONSE__:"):
                    try:
                        _, from_user, to_user, response, public_key = data.split(":", 4)
                        for conn, name in self.connections.items():
                            if name == to_user and conn != ws:
                                await conn.send_text(f"__CONNECT_RESPONSE__:{from_user}:{to_user}:{response}:{public_key}")
                                self.message_received.emit(f"📤 Ответ на подключение от {from_user} к {to_user}: {response} с ключом {public_key}")
                                if response == "ACCEPT":
                                    await ws.send_text(f"__CONNECT_SUCCESS__:{to_user}")
                                    await conn.send_text(f"__CONNECT_SUCCESS__:{from_user}")
                                    self.message_received.emit(f"📤 Успешное подключение между {from_user} и {to_user}")
                                break
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат ответа на подключение: {data}")
                        continue

                elif data.startswith("__TO__:"):
                    try:
                        _, target_name, message = data.split(":", 2)
                        for conn, name in self.connections.items():
                            if name == target_name and conn != ws:
                                await conn.send_text(f"{username}:{message}")
                                self.message_received.emit(f"📤 Сообщение от {username} к {target_name}: {message}")
                                break
                    except ValueError:
                        self.message_received.emit(f"⚠️ Некорректный формат сообщения: {data}")
                        continue

                else:
                    for conn in self.connections:
                        if conn != ws:
                            await conn.send_text(f"{username}:{data}")
                            self.message_received.emit(f"📤 Сообщение от {username} всем: {data}")

        except Exception as e:
            if username:
                self.message_received.emit(f"🔌 Пользователь {username} отключён: {str(e)}")
            else:
                self.message_received.emit(f"🔌 Клиент отключён: {str(e)}")
            self.connections.pop(ws, None)

    def run(self):
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/get_params")(self.get_params)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        config = Config(app=self.app, host="127.0.0.1", port=8000, loop=loop)
        server = Server(config=config)
        loop.run_until_complete(server.serve())