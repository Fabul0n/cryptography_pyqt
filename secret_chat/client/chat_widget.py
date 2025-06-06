from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QListWidgetItem, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from secret_chat.client.websocket_client import WebSocketClient
from secret_chat.client.connect_dialog import ConnectToUserDialog
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
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
        self.rsa_public_key = None
        self.loop = loop
        self.des_key = None
        self.public_keys = {}
        self.rsa_public_keys = {}
        self.manual_mode = False
        self.pending_message = None

        layout = QVBoxLayout()

        self.status_label = QLabel("Статус: Подключение...")
        layout.addWidget(self.status_label)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setReadOnly(True)
        self.secret_key_input.setPlaceholderText("Общий секретный ключ")
        layout.addWidget(QLabel("Общий секретный ключ:"))
        layout.addWidget(self.secret_key_input)

        self.manual_mode_checkbox = QCheckBox("Ручной режим")
        self.manual_mode_checkbox.toggled.connect(self.toggle_manual_mode)
        layout.addWidget(self.manual_mode_checkbox)

        self.manual_verify_widget = QWidget()
        manual_layout = QVBoxLayout()
        self.encrypted_message_input = QLineEdit()
        self.encrypted_message_input.setPlaceholderText("Зашифрованное сообщение")
        manual_layout.addWidget(QLabel("Зашифрованное сообщение:"))
        manual_layout.addWidget(self.encrypted_message_input)
        self.signature_input = QLineEdit()
        self.signature_input.setPlaceholderText("Цифровая подпись")
        manual_layout.addWidget(QLabel("Цифровая подпись:"))
        manual_layout.addWidget(self.signature_input)
        self.verify_button = QPushButton("Проверить цифровую подпись")
        self.verify_button.clicked.connect(self.verify_manual_signature)
        manual_layout.addWidget(self.verify_button)
        self.manual_verify_widget.setLayout(manual_layout)
        self.manual_verify_widget.setVisible(False)
        layout.addWidget(self.manual_verify_widget)

        self.select_recipient_button = QPushButton("OK")
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
        self.websocket_client.key_received.connect(self.store_public_keys)
        self.websocket_client.error_occurred.connect(self.show_error)
        self.websocket_client.connect_request_received.connect(self.handle_connect_request)
        asyncio.ensure_future(self.websocket_client.connect_and_listen(), loop=self.loop)

    def toggle_manual_mode(self, checked):
        self.manual_mode = checked
        #print(f"{self.username}: Ручной режим {'включен' if self.manual_mode else 'выключен'}")
        self.manual_verify_widget.setVisible(self.manual_mode)
        if not self.manual_mode and self.pending_message:
            self.process_pending_message()

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

    def verify_signature(self, message, signature, rsa_public_key):
        try:
            rsa_key = RSA.import_key(base64.b64decode(rsa_public_key))
            h = SHA256.new(message.encode())
            verifier = PKCS1_v1_5.new(rsa_key)
            return verifier.verify(h, base64.b64decode(signature))
        except Exception as e:
            self.show_error(f"Ошибка проверки подписи: {e}")
            return False

    def verify_manual_signature(self):
        if not self.pending_message:
            self.show_error("Нет ожидающего сообщения для проверки")
            return
        sender, encrypted_message, signature = self.pending_message
        entered_message = self.encrypted_message_input.text()
        entered_signature = self.signature_input.text()
        if not entered_message or not entered_signature:
            self.show_error("Заполните поля сообщения и подписи")
            return
        if entered_message != encrypted_message or entered_signature != signature:
            self.show_error("Введенные данные не совпадают с полученными")
            return
        decrypted_content = self.decrypt_message(encrypted_message)
        #print(f"{self.username} расшифровал сообщение для проверки: {decrypted_content}")
        message_to_verify = f"{sender}:{decrypted_content}"
        if self.verify_signature(message_to_verify, signature, self.rsa_public_keys.get(sender)):
            current_time = datetime.datetime.now().strftime("%H:%M")
            item = QListWidgetItem(f"[{current_time}] {sender}: {decrypted_content}")
            item.setFont(QFont("Arial", 10))
            item.setForeground(QColor("blue"))
            self.history_list.addItem(item)
            self.history_list.scrollToBottom()
            self.pending_message = None
            self.encrypted_message_input.clear()
            self.signature_input.clear()
        else:
            self.show_error(f"Неверная подпись от {sender}")

    def process_pending_message(self):
        if not self.pending_message:
            return
        sender, encrypted_message, signature = self.pending_message
        decrypted_content = self.decrypt_message(encrypted_message)
        #print(f"{self.username} расшифровал сообщение для автоматической проверки: {decrypted_content}")
        message_to_verify = f"{sender}:{decrypted_content}"
        if self.verify_signature(message_to_verify, signature, self.rsa_public_keys.get(sender)):
            current_time = datetime.datetime.now().strftime("%H:%M")
            item = QListWidgetItem(f"[{current_time}] {sender}: {decrypted_content}")
            item.setFont(QFont("Arial", 10))
            item.setForeground(QColor("blue"))
            self.history_list.addItem(item)
            self.history_list.scrollToBottom()
        else:
            self.show_error(f"Неверная подпись от {sender}")
        self.pending_message = None

    def select_recipient(self):
        dialog = ConnectToUserDialog(self)
        if dialog.exec():
            self.recipient_name = dialog.get_target_name()
            public_key = self.websocket_client.get_public_key()
            rsa_public_key = self.websocket_client.get_rsa_public_key()
            if public_key is None or rsa_public_key is None:
                self.show_error("Ключи не сгенерированы")
                return
            message = f"{self.username}:{self.recipient_name}:{public_key}"
            signature = self.websocket_client.sign_message(message)
            self.websocket_client.send_message(f"__CONNECT_REQUEST__:{self.username}:{self.recipient_name}:{public_key}:{rsa_public_key}:{signature}")
            self.status_label.setText(f"Ожидание ответа от: {self.recipient_name}")

    def store_public_keys(self, name, public_key):
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
        #print(f"{self.username} вычислил shared_secret для {other_user}: {self.shared_secret} с public_key={public_key}, a={self.a}, p={self.p}")
        if self.shared_secret:
            self.secret_key_input.setText(str(self.shared_secret))
        return True

    def handle_connect_request(self, from_user, to_user, data):
        if to_user != self.username:
            return
        try:
            public_key, rsa_public_key, signature = data.split(":")
            public_key = int(public_key)
            message = f"{from_user}:{to_user}:{public_key}"
            if not self.verify_signature(message, signature, rsa_public_key):
                self.show_error(f"Неверная подпись от {from_user}")
                return
        except ValueError:
            self.show_error(f"Некорректные данные запроса от {from_user}: {data}")
            return
        #print(f"{self.username} получил запрос от {from_user} с public_key={public_key}, rsa_public_key={rsa_public_key}")
        reply = QMessageBox.question(
            self,
            "Запрос на подключение",
            f"Пользователь {from_user} хочет к вам подключиться",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        response = "ACCEPT" if reply == QMessageBox.StandardButton.Yes else "REJECT"
        my_public_key = self.websocket_client.get_public_key()
        my_rsa_public_key = self.websocket_client.get_rsa_public_key()
        if my_public_key is None or my_rsa_public_key is None:
            self.show_error("Ключи не сгенерированы")
            return
        self.public_keys[from_user] = public_key
        self.rsa_public_keys[from_user] = rsa_public_key
        #print(f"{self.username} сохранил public_key для {from_user}: {public_key}, rsa_public_key={rsa_public_key}")
        message = f"{self.username}:{from_user}:{response}:{my_public_key}"
        signature = self.websocket_client.sign_message(message)
        self.websocket_client.send_message(f"__CONNECT_RESPONSE__:{self.username}:{from_user}:{response}:{my_public_key}:{my_rsa_public_key}:{signature}")
        if response == "ACCEPT":
            self.recipient_name = from_user
            self.status_label.setText(f"Ожидание подтверждения от: {from_user}")

    def add_to_history(self, message: str):
        current_time = datetime.datetime.now().strftime("%H:%M")
        item = QListWidgetItem()
        try:
            #print(f"{self.username} обрабатывает сообщение: {message}")
            if message.startswith("__CONNECT_RESPONSE__:"):
                parts = message.split(":")
                if len(parts) != 7:
                    raise ValueError(f"Некорректный формат CONNECT_RESPONSE: {message}")
                from_user, to_user, response, public_key, rsa_public_key, signature = parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                public_key = int(public_key)
                message_to_verify = f"{from_user}:{to_user}:{response}:{public_key}"
                if not self.verify_signature(message_to_verify, signature, rsa_public_key):
                    self.show_error(f"Неверная подпись от {from_user} в CONNECT_RESPONSE")
                    return
                #print(f"{self.username} получил public_key от {from_user} в CONNECT_RESPONSE: {public_key}, rsa_public_key={rsa_public_key}")
                if response == "ACCEPT":
                    self.recipient_name = from_user
                    self.public_keys[from_user] = public_key
                    self.rsa_public_keys[from_user] = rsa_public_key
                    #print(f"{self.username} сохранил public_key для {from_user}: {public_key}, rsa_public_key={rsa_public_key}")
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
                #print(f"{self.username} использует public_key для {other_user}: {self.public_keys[other_user]}")
                if not self.compute_shared_secret(other_user, self.public_keys[other_user]):
                    return
                self.status_label.setText(f"Подключено к: {other_user}")
                item.setText(f"[{current_time}] Система: Подключение с {other_user} установлено")
                item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                item.setForeground(QColor("darkGreen"))
            elif ":" in message:
                parts = message.split(":", 3)
                if len(parts) != 4:
                    raise ValueError(f"Некорректный формат сообщения: {message}")
                sender, reciever, encrypted_message, signature = parts
                #print(f"{self.username} получил сообщение от {sender}: encrypted_message={encrypted_message}, signature={signature}")
                if sender == self.username:
                    return
                if sender not in self.rsa_public_keys:
                    self.show_error(f"RSA публичный ключ для {sender} не найден")
                    return
                if self.manual_mode:
                    if self.pending_message:
                        #print(f"{self.username}: Пропущено сообщение от {sender}, так как есть непроверенное сообщение")
                        return
                    self.pending_message = (sender, encrypted_message, signature)
                    self.encrypted_message_input.setText(encrypted_message)
                    self.signature_input.setText(signature)
                    #print(f"{self.username} заполнил поля: encrypted_message={encrypted_message}, signature={signature}")
                    item.setText(f"[{current_time}] Система: Получено сообщение от {sender}, ожидает ручной проверки")
                    item.setFont(QFont("Arial", 10, QFont.Weight.Normal, italic=True))
                    item.setForeground(QColor("darkGray"))
                else:
                    decrypted_content = self.decrypt_message(encrypted_message)
                    #print(f"{self.username} расшифровал сообщение: {decrypted_content}")
                    message_to_verify = f"{sender}:{decrypted_content}"
                    if self.verify_signature(message_to_verify, signature, self.rsa_public_keys[sender]):
                        item.setText(f"[{current_time}] {sender}: {decrypted_content}")
                        item.setFont(QFont("Arial", 10))
                        item.setForeground(QColor("blue"))
                    else:
                        self.show_error(f"Неверная подпись от {sender}")
                        return
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
        message_to_sign = f"{self.username}:{msg}"
        #print(f"{self.username} подписывает сообщение: {message_to_sign}")
        signature = self.websocket_client.sign_message(message_to_sign)
        self.websocket_client.send_message(f"{self.recipient_name}:{encrypted_msg}:{signature}")
        self.message_input.clear()

    def show_error(self, error):
        QMessageBox.critical(self, "Ошибка", error)