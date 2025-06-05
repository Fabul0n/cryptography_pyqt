from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QListWidget
from secret_chat.server.server_no_gui import WebSocketServer


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket Сервер")
        self.resize(600, 500)

        layout = QVBoxLayout()
        self.status = QLabel("Сервер запущен")
        layout.addWidget(self.status)

        self.log = QListWidget()
        layout.addWidget(self.log)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server_thread = WebSocketServer()
        self.server_thread.message_received.connect(self.update_log)
        self.server_thread.start()

    def update_log(self, msg):
        self.log.addItem(msg)