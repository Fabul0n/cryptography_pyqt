from PyQt6.QtWidgets import (
    QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QMessageBox, QDialog, QLineEdit, QHBoxLayout
)
import asyncio

from widgets.secret_chat.client.key_generation import KeyGenerationDialog
from widgets.secret_chat.client.websocket_client import WebSocketClient

from hashlib import md5


def encrypt_bytes(message: str, public_key):
    e, n = public_key
    return [pow(b, e, n) for b in message.encode('utf-8')]


def decrypt_bytes(ciphertext, private_key):
    d, n = private_key
    byte_data = bytearray()
    for c in ciphertext:
        decrypted_byte = pow(c, d, n)
        if not (0 <= decrypted_byte <= 255):
            raise ValueError(f"Расшифрованное значение {decrypted_byte} вне диапазона байта")
        byte_data.append(decrypted_byte)
    return byte_data.decode('utf-8', errors='replace')

class ChatWidget(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"RSA - {username}")
        self.resize(500, 800)
        self.username = username
        self.reciever_name = None
        self.reciever_public_key = None

        layout = QVBoxLayout()
        encrypt_layout = QVBoxLayout()
        decrypt_layout = QVBoxLayout()
        crypt_layout = QHBoxLayout()

        self.status_label = QLabel("Статус: Не подключено")
        layout.addWidget(self.status_label)

        self.set_keys_button = QPushButton("Настроить ключи")
        self.set_keys_button.clicked.connect(self.open_key_dialog)
        layout.addWidget(self.set_keys_button)

        self.sender_key = QLabel("Ваш ключ:")
        self.sender_key.setWordWrap(True)
        self.sender_key_text = QLineEdit()
        self.sender_key_text.setReadOnly(True)
        self.sender_key_text.adjustSize()
        layout.addWidget(self.sender_key)
        layout.addWidget(self.sender_key_text)

        self.reciever_key = QLabel("Ключ получателя:")
        self.reciever_key.setWordWrap(True)
        self.reciever_key_text = QLineEdit()
        self.reciever_key_text.setReadOnly(True)
        self.reciever_key_text.adjustSize()
        layout.addWidget(self.reciever_key)
        layout.addWidget(self.reciever_key_text)

        self.message_label = QLabel("Сообщение:")
        self.message_input = QTextEdit()
        layout.addWidget(self.message_label)
        layout.addWidget(self.message_input)

        self.signature_label = QLabel("Цифровая подпись:")
        self.signature_label.setWordWrap(True)
        self.signature_text = QLineEdit()
        self.signature_text.setReadOnly(True)
        self.signature_text.adjustSize()
        layout.addWidget(self.signature_label)
        layout.addWidget(self.signature_text)

        self.calc_sign_button = QPushButton("Вычислить цифровую подпись")
        self.calc_sign_button.clicked.connect(self.calc_signature)
        layout.addWidget(self.calc_sign_button)

        self.encrypt_button = QPushButton("Зашифровать")
        self.encrypt_button.clicked.connect(self.encrypt_message)
        encrypt_layout.addWidget(self.encrypt_button)

        self.send_button = QPushButton("Отправить сообщение")
        self.send_button.clicked.connect(self.send_to_other)
        encrypt_layout.addWidget(self.send_button)

        self.decrypt_button = QPushButton("Расшифровать")
        self.decrypt_button.clicked.connect(self.decrypt_received)
        decrypt_layout.addWidget(self.decrypt_button)

        self.check_sign_button = QPushButton("Проверить цифровую подпись")
        self.check_sign_button.clicked.connect(self.check_signature)
        decrypt_layout.addWidget(self.check_sign_button)

        crypt_layout.addLayout(encrypt_layout)
        crypt_layout.addLayout(decrypt_layout)
        layout.addLayout(crypt_layout)
        self.setLayout(layout)

        self.public_key = None
        self.private_key = None
        self.reciever_name = None
        self.reciever_public_key = None
        self.websocket_client = WebSocketClient(username, self)

        self.websocket_client.message_received.connect(self.receive_encrypted_message)
        self.websocket_client.key_received.connect(self.set_reciever)
        self.websocket_client.start()

    def hash_msg(self):
        if not self.public_key:
            QMessageBox.critical(self, "Ошибка", "Сначала настройте свои ключи!")
            return

        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.critical(self, "Ошибка", "Введите сообщение для шифрования!")
            return
        
        return md5(message.encode()).hexdigest()

    def calc_signature(self):      
        hashed = self.hash_msg()

        sign = encrypt_bytes(hashed, self.private_key)
        self.signature_text.setText(",".join(map(str, sign)))

    def check_signature(self):
        sign = self.signature_text.text()

        hashed = decrypt_bytes(list(map(int, sign.split(","))), self.reciever_public_key)

        if hashed == self.hash_msg():
            QMessageBox.information(self, "Успех!", "Электронная подпись верна!")
        else:
            QMessageBox.critical(self, "Ошибка!", "Электронная подпись неверна!")

    def set_reciever(self, name, public_key):
        self.reciever_name = name
        self.reciever_public_key = public_key
        if self.reciever_key_text.text() == f"({public_key[0]}, {public_key[1]})":
            return
        self.setWindowTitle(f"RSA - {self.username} → {name}")
        self.status_label.setText(f"Подключено к: {name}")

        self.reciever_key_text.setText(f"({public_key[0]}, {public_key[1]})")

        if self.public_key:
            self.send_public_key()

    def open_key_dialog(self):
        dialog = KeyGenerationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            p, q, e = dialog.get_values()
            self.generate_rsa_keys(p, q, e)
            self.sender_key_text.setText(f"({self.public_key[0]}, {self.public_key[1]})")

            self.send_public_key()

    def generate_rsa_keys(self, p, q, e):
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        if (d is None) or ((e * d) % phi != 1):
            raise ValueError("Ошибка генерации ключей")
        self.public_key = (e, p * q)
        self.private_key = (d, p * q)

    def send_public_key(self):
        try:
            asyncio.run(self.websocket_client._send_message_coroutine(
                f"__HELLO__:{self.username}:{self.public_key[0]}:{self.public_key[1]}"
            ))
        except Exception as e:
            print("Ошибка при отправке ключа:", e)

    def encrypt_message(self):
        if not self.reciever_public_key:
            QMessageBox.critical(self, "Ошибка", "Не указан публичный ключ собеседника!")
            return

        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.critical(self, "Ошибка", "Введите сообщение для шифрования!")
            return

        encrypted = encrypt_bytes(message, self.reciever_public_key)
        self.message_input.setText(",".join(map(str, encrypted)))

    def decrypt_received(self):
        try:
            text = self.message_input.toPlainText()
            if not text:
                raise ValueError("Сообщение пустое")
            ciphertext = list(map(int, text.split(",")))
            decrypted = decrypt_bytes(ciphertext, self.private_key)
            self.message_input.setText(decrypted)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расшифрования: {str(e)}")

    def send_to_other(self):
        encrypted_text = self.message_input.toPlainText()
        if not encrypted_text:
            QMessageBox.critical(self, "Ошибка", "Нет сообщения для отправки!")
            return
        sign = self.signature_text.text()
        if not sign:
            QMessageBox.critical(self, "Ошибка", "Нет подписи!")
            return
        self.websocket_client.send_message(f"{encrypted_text}:{sign}")

    def receive_encrypted_message(self, message):
        encrypted, sign = message.split(':')
        self.message_input.setText(encrypted)
        self.signature_text.setText(sign)