import sys
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QCheckBox,
    QVBoxLayout, QWidget, QLabel, QListWidget, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from fastapi import FastAPI, WebSocket
from uvicorn import Config, Server
from websockets.exceptions import ConnectionClosed


class WebSocketServer(QThread):
    message_received = pyqtSignal(str)
    request_send_button_update = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.active_connections = []
        self.message_queue = []
        self.intercept_mode = False
        self.loop = None

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        self.message_received.emit("🔌 Клиент подключён")
        if len(self.active_connections) >= 2:
            await websocket.send_text("Сервер заполнен.")
            await websocket.close(code=4000)
            return
        self.active_connections.append(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                print(f"Получено от клиента: {data}")
                self.message_received.emit(f"📥 Получено: {data}")

                if self.intercept_mode:
                    self.message_queue.append((websocket, data))
                    self.request_send_button_update.emit()
                else:
                    for conn in self.active_connections:
                        if conn != websocket:
                            await conn.send_text(data)
        except ConnectionClosed:
            self.active_connections.remove(websocket)
            self.message_received.emit("🔌 Клиент отключён")

    def run_server(self):
        self.loop = asyncio.new_event_loop()
        config = Config(app=self.app, host="127.0.0.1", port=8000, loop=self.loop)
        server = Server(config=config)
        self.loop.run_until_complete(server.serve())

    def run(self):
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.run_server()

    def send_stored_message(self):
        if not self.message_queue:
            self.message_received.emit("Нет сообщений в очереди")
            return

        sender, message = self.message_queue.pop(0)
        self.message_received.emit(f"Передано дальше: {message}")

        recipients = [conn for conn in self.active_connections if conn != sender]
        if not recipients:
            self.message_received.emit("Нет получателя для сообщения")
            return

        recipient = recipients[0]

        asyncio.run_coroutine_threadsafe(recipient.send_text(message), self.loop)


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket Сервер")
        self.resize(600, 500)

        layout = QVBoxLayout()

        self.status_label = QLabel("Статус: Сервер запущен")
        layout.addWidget(self.status_label)

        self.intercept_checkbox = QCheckBox("Перехват сообщений")
        layout.addWidget(self.intercept_checkbox)

        self.send_button = QPushButton("Отправить сообщение дальше")
        self.send_button.setEnabled(False)
        layout.addWidget(self.send_button)

        self.history_list = QListWidget()
        layout.addWidget(QLabel("История сообщений:"))
        layout.addWidget(self.history_list)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server_thread = WebSocketServer()
        self.server_thread.message_received.connect(self.add_to_history)
        self.server_thread.request_send_button_update.connect(lambda: self.send_button.setEnabled(True))
        self.intercept_checkbox.toggled.connect(self.toggle_intercept)
        self.send_button.clicked.connect(self.server_thread.send_stored_message)

        self.server_thread.start()

    def add_to_history(self, message):
        self.history_list.addItem(message)

    def toggle_intercept(self, checked):
        self.server_thread.intercept_mode = checked
        self.send_button.setEnabled(checked)
        status = "включён" if checked else "выключен"
        QMessageBox.information(self, "Режим перехвата", f"Режим перехвата {status}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerGUI()
    window.show()
    sys.exit(app.exec())