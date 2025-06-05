from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from secret_chat.client.websocket_client import WebSocketClient
from secret_chat.client.connect_dialog import ConnectToUserDialog
import datetime
import asyncio


class ChatWidget(QWidget):
    def __init__(self, username, loop):
        super().__init__()
        self.setWindowTitle(f"Диффи-Хеллман — {username}")
        self.resize(500, 600)
        self.username = username
        self.recipient_name = None
        self.B = None
        self.shared_secret = None
        self.p = None
        self.a = None
        self.loop = loop

        layout = QVBoxLayout()

        self.status_label = QLabel("Статус: Подключение...")
        layout.addWidget(self.status_label)

        self.select_recipient_button = QPushButton("Выбрать получателя")
        self.select_recipient_button.clicked.connect(self.select_recipient)
        layout.addWidget(self.select_recipient_button)

        self.history_list = QListWidget()
        layout.addWidget(QLabel("История сообщений:"))
        layout.addWidget(self.history_list)

        self.message_input = QTextEdit()
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.websocket_client = WebSocketClient(username, self, loop)
        self.websocket_client.message_received.connect(self.add_to_history)
        self.websocket_client.key_received.connect(self.set_recipient_key)
        self.websocket_client.error_occurred.connect(self.show_error)
        self.websocket_client.connect_request_received.connect(self.handle_connect_request)
        asyncio.ensure_future(self.websocket_client.connect_and_listen(), loop=self.loop)

    def select_recipient(self):
        dialog = ConnectToUserDialog(self)
        if dialog.exec():
            self.recipient_name = dialog.get_target_name()
            self.websocket_client.send_message(f"__CONNECT_REQUEST__:{self.username}:{self.recipient_name}")
            self.status_label.setText(f"Ожидание ответа от: {self.recipient_name}")

    def set_recipient_key(self, name, public_key):
        self.B = public_key[0]
        self.shared_secret = pow(self.B, self.a, self.p)
        if self.recipient_name == name:
            self.status_label.setText(f"Подключено к: {name}")

    def handle_connect_request(self, from_user, to_user):
        if to_user != self.username:
            return
        reply = QMessageBox.question(
            self,
            "Запрос на подключение",
            f"Пользователь {from_user} хочет к вам подключиться. Согласиться?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        response = "ACCEPT" if reply == QMessageBox.StandardButton.Yes else "REJECT"
        self.websocket_client.send_message(f"__CONNECT_RESPONSE__:{self.username}:{from_user}:{response}")
        if response == "ACCEPT":
            self.recipient_name = from_user
            self.status_label.setText(f"Подключено к: {from_user}")

    def add_to_history(self, message):
        current_time = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem()
        if message.startswith("__CONNECT_RESPONSE__:"):
            _, from_user, response = message.split(":", 3)
            if response == "ACCEPT":
                self.recipient_name = from_user
                self.status_label.setText(f"Подключено к: {from_user}")
                item.setText(f"[{current_time}] Система: Подключение с {from_user} установлено")
                item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                item.setForeground(QColor("darkGreen"))
            else:
                self.status_label.setText("Статус: Подключение отклонено")
                item.setText(f"[{current_time}] Система: {from_user} отклонил подключение")
                item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                item.setForeground(QColor("red"))
        elif ":" in message:
            sender, content = message.split(":", 1)
            if sender == self.username:
                return
            item.setText(f"[{current_time}] {sender}: {content}")
            item.setFont(QFont("Arial", 10))
            item.setForeground(QColor("blue"))
        else:
            item.setText(f"[{current_time}] Система: {message}")
            item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
            item.setForeground(QColor("darkGray"))
        self.history_list.addItem(item)
        self.history_list.scrollToBottom()

    def send_message(self):
        msg = self.message_input.toPlainText().strip()
        if not msg:
            return
        if not self.recipient_name:
            QMessageBox.warning(self, "Ошибка", "Выберите получателя!")
            return
        current_time = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem(f"[{current_time}] Вы → {self.recipient_name}: {msg}")
        item.setFont(QFont("Arial", 10))
        item.setForeground(QColor("darkGreen"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.history_list.addItem(item)
        self.history_list.scrollToBottom()
        self.websocket_client.send_message(f"__TO__:{self.recipient_name}:{msg}")
        self.message_input.clear()

    def show_error(self, error):
        QMessageBox.critical(self, "Ошибка", error)