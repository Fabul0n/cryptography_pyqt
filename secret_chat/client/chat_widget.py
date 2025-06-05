from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from secret_chat.client.websocket_client import WebSocketClient
from secret_chat.client.connect_dialog import ConnectToUserDialog
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256
import datetime
import asyncio
import base64


class ChatWidget(QWidget):
    def __init__(self, username, loop):
        super().__init__()
        self.setWindowTitle(f"Диффи-Хеллман — {username}")
        self.resize(700, 600)
        self.username = username
        self.recipient_name = None
        self.shared_secret = None
        self.p = None
        self.g = None
        self.a = None
        self.loop = loop
        self.des_key = None
        self.public_keys = {}

        layout = QVBoxLayout()

        self.status_label = QLabel("Статус: Подключение...")
        layout.addWidget(self.status_label)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setReadOnly(True)
        self.secret_key_input.setPlaceholderText("Общий секретный ключ")
        layout.addWidget(QLabel("Общий секретный ключ:"))
        layout.addWidget(self.secret_key_input)

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
        self.websocket_client.key_received.connect(self.store_public_key)
        self.websocket_client.error_occurred.connect(self.show_error)
        self.websocket_client.connect_request_received.connect(self.handle_connect_request)
        asyncio.ensure_future(self.websocket_client.connect_and_listen(), loop=self.loop)

    def derive_des_key(self):
        if self.shared_secret is None:
            return None
        secret_bytes = str(self.shared_secret).encode()
        hashed = sha256(secret_bytes).digest()
        return hashed[:8]

    def encrypt_message(self, message):
        if not self.des_key:
            return message
        cipher = DES.new(self.des_key, DES.MODE_CBC, iv=b'12345678')
        padded = pad(message.encode(), DES.block_size)
        ciphertext = cipher.encrypt(padded)
        return base64.b64encode(ciphertext).decode()

    def decrypt_message(self, encrypted_message):
        if not self.des_key:
            return encrypted_message
        try:
            cipher = DES.new(self.des_key, DES.MODE_CBC, iv=b'12345678')
            ciphertext = base64.b64decode(encrypted_message)
            padded = cipher.decrypt(ciphertext)
            return unpad(padded, DES.block_size).decode()
        except Exception as e:
            self.show_error(f"Ошибка дешифрования: {e}")
            return encrypted_message

    def select_recipient(self):
        dialog = ConnectToUserDialog(self)
        if dialog.exec():
            self.recipient_name = dialog.get_target_name()
            public_key = self.websocket_client.get_public_key()
            if public_key is None:
                self.show_error("Публичный ключ не сгенерирован")
                return
            self.websocket_client.send_message(f"__CONNECT_REQUEST__:{self.username}:{self.recipient_name}:{public_key}")
            self.status_label.setText(f"Ожидание ответа от: {self.recipient_name}")

    def store_public_key(self, name, public_key):
        pass

    def compute_shared_secret(self, other_user, public_key):
        if public_key is None or self.a is None or self.p is None:
            self.show_error(f"Невозможно вычислить общий секрет для {other_user}: public_key={public_key}, a={self.a}, p={self.p}")
            return False
        if public_key < 0:
            self.show_error(f"Отрицательный публичный ключ для {other_user}: {public_key}")
            return False
        self.public_keys[other_user] = public_key
        self.shared_secret = pow(public_key, self.a, self.p)
        self.des_key = self.derive_des_key()
        print(f"{self.username} вычислил shared_secret для {other_user}: {self.shared_secret} с public_key={public_key}, a={self.a}, p={self.p}")
        if self.shared_secret:
            self.secret_key_input.setText(str(self.shared_secret))
        return True

    def handle_connect_request(self, from_user, to_user, public_key):
        if to_user != self.username:
            return
        try:
            public_key = int(public_key)
        except ValueError:
            self.show_error(f"Некорректный публичный ключ от {from_user}: {public_key}")
            return
        print(f"{self.username} получил запрос от {from_user} с public_key={public_key}")
        reply = QMessageBox.question(
            self,
            "Запрос на подключение",
            f"Пользователь {from_user} хочет к вам подключиться",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        response = "ACCEPT" if reply == QMessageBox.StandardButton.Yes else "REJECT"
        my_public_key = self.websocket_client.get_public_key()
        if my_public_key is None:
            self.show_error("Публичный ключ не сгенерирован")
            return
        self.public_keys[from_user] = public_key
        print(f"{self.username} сохранил public_key для {from_user}: {public_key}")
        self.websocket_client.send_message(f"__CONNECT_RESPONSE__:{self.username}:{from_user}:{response}:{my_public_key}")
        if response == "ACCEPT":
            self.recipient_name = from_user
            self.status_label.setText(f"Ожидание подтверждения от: {from_user}")

    def add_to_history(self, message):
        current_time = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem()
        try:
            print(f"{self.username} обрабатывает сообщение: {message}")
            if message.startswith("__CONNECT_RESPONSE__:"):
                parts = message.split(":")
                if len(parts) != 5:
                    raise ValueError(f"Некорректный формат CONNECT_RESPONSE: {message}")
                from_user, to_user, response, public_key = parts[1], parts[2], parts[3], parts[4]
                public_key = int(public_key)
                print(f"{self.username} получил public_key от {from_user} в CONNECT_RESPONSE: {public_key}")
                if response == "ACCEPT":
                    self.recipient_name = from_user
                    self.public_keys[from_user] = public_key
                    print(f"{self.username} сохранил public_key для {from_user}: {public_key}")
                    self.status_label.setText(f"Ожидание подтверждения от: {from_user}")
                    item.setText(f"[{current_time}] Система: Ожидание подтверждения от {from_user}")
                    item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                    item.setForeground(QColor("darkGray"))
                else:
                    self.status_label.setText("Статус: Подключение отклонено")
                    item.setText(f"[{current_time}] Система: {from_user} отклонил подключение")
                    item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                    item.setForeground(QColor("red"))
            elif message.startswith("__CONNECT_SUCCESS__:"):
                _, other_user = message.split(":", 1)
                self.recipient_name = other_user
                if other_user not in self.public_keys:
                    self.show_error(f"Публичный ключ для {other_user} не найден")
                    return
                print(f"{self.username} использует public_key для {other_user}: {self.public_keys[other_user]}")
                if not self.compute_shared_secret(other_user, self.public_keys[other_user]):
                    return
                self.status_label.setText(f"Подключено к: {other_user}")
                item.setText(f"[{current_time}] Система: Подключение с {other_user} установлено")
                item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                item.setForeground(QColor("darkGreen"))
            elif ":" in message:
                sender, content = message.split(":", 1)
                if sender == self.username:
                    return
                decrypted_content = self.decrypt_message(content)
                item.setText(f"[{current_time}] {sender}: {decrypted_content}")
                item.setFont(QFont("Arial", 10))
                item.setForeground(QColor("blue"))
            else:
                item.setText(f"[{current_time}] Система: {message}")
                item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                item.setForeground(QColor("darkGray"))
        except Exception as e:
            self.show_error(f"Ошибка обработки сообщения: {e}")
        self.history_list.addItem(item)
        self.history_list.scrollToBottom()

    def send_message(self):
        msg = self.message_input.toPlainText().strip()
        if not msg:
            return
        if not self.recipient_name:
            QMessageBox.critical(self, "Ошибка", "Выберите получателя!")
            return
        current_time = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem(f"[{current_time}] Вы → {self.recipient_name}: {msg}")
        item.setFont(QFont("Arial", 10))
        item.setForeground(QColor("darkGreen"))
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.history_list.addItem(item)
        self.history_list.scrollToBottom()
        encrypted_msg = self.encrypt_message(msg)
        self.websocket_client.send_message(f"__TO__:{self.recipient_name}:{encrypted_msg}")
        self.message_input.clear()

    def show_error(self, error):
        QMessageBox.critical(self, "Ошибка", error)