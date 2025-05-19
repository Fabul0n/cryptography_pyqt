import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from sympy import isprime as is_prime
from sympy import nextprime
from math import gcd

from hashlib import sha256


def mod_inverse(a, m):
    if gcd(a, m) != 1:
        return None
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1


def encrypt_bytes(message, public_key):
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


class KeyGenerationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация ключей")

        self.p_input = QLineEdit()
        self.q_input = QLineEdit()
        self.e_input = QLineEdit()

        layout = QFormLayout()

        self.generate_pq_button = QPushButton("Сгенерировать p и q")
        self.generate_pq_button.clicked.connect(self.generate_pq)

        self.generate_e_button = QPushButton("Сгенерировать e")
        self.generate_e_button.clicked.connect(self.generate_e)

        layout.addRow("Сгенерировать p и q", self.generate_pq_button)
        layout.addRow("p:", self.p_input)
        layout.addRow("q:", self.q_input)
        layout.addRow("Сгенерировать e", self.generate_e_button)
        layout.addRow("e:", self.e_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)

        layout.addRow(self.buttons)

        self.setLayout(layout)

    def generate_pq(self):
        self.p_input.setText(str(nextprime(random.randint(10**20, 10**100))))
        self.q_input.setText(str(nextprime(random.randint(10**20, 10**100))))

    def generate_e(self):
        try:
            p = int(self.p_input.text())
            q = int(self.q_input.text())
            phi = (p - 1) * (q - 1)
            e = random.randint(2, phi - 1)
            while gcd(e, phi) != 1:
                e = random.randint(2, phi - 1)
            self.e_input.setText(str(e))
        except:
            QMessageBox.critical(self, "Ошибка", "Сначала введите корректные p и q!")

    def get_values(self):
        try:
            p = int(self.p_input.text())
            q = int(self.q_input.text())
            e = int(self.e_input.text())
            return p, q, e
        except:
            return None, None, None

    def validate_and_accept(self):
        p, q, e = self.get_values()
        if not p or not q or not e:
            QMessageBox.critical(self, "Ошибка", "Все поля должны содержать числовые значения.")
            return False

        if p <= 1 or q <= 1:
            QMessageBox.critical(self, "Ошибка", "p и q должны быть больше 1.")
            return False

        if not is_prime(p):
            QMessageBox.critical(self, "Ошибка", f"p = {p} не является простым числом.")
            return False

        if not is_prime(q):
            QMessageBox.critical(self, "Ошибка", f"q = {q} не является простым числом.")
            return False

        if p == q:
            QMessageBox.critical(self, "Ошибка", "p и q не могут быть равны.")
            return False

        phi = (p - 1) * (q - 1)
        if e <= 1 or e >= phi:
            QMessageBox.critical(self, "Ошибка", f"e должно быть в диапазоне: 1 < e < {phi}")
            return False

        if gcd(e, phi) != 1:
            QMessageBox.critical(self, "Ошибка", f"e = {e} не взаимно просто с phi = {phi}")
            return False

        self.accept()


class UserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA - User")
        self.setGeometry(700, 100, 500, 400)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.set_keys_button = QPushButton("Настроить ключи")
        self.set_keys_button.clicked.connect(self.open_key_dialog)
        layout.addWidget(self.set_keys_button)

        self.keys_label = QLabel("Ключи не заданы")
        self.keys_label.setWordWrap(True)
        layout.addWidget(self.keys_label)

        self.message_label = QLabel("Получено/отправлено сообщение:")
        self.message_input = QTextEdit()
        layout.addWidget(self.message_label)
        layout.addWidget(self.message_input)

        self.encrypt_button = QPushButton("Получить хэш")
        self.encrypt_button.clicked.connect(self.hash_message)
        layout.addWidget(self.encrypt_button)

        self.hash_label = QLabel("Хэш сообщения:")
        self.hash_input = QTextEdit()
        layout.addWidget(self.hash_label)
        layout.addWidget(self.hash_input)

        self.encrypt_button = QPushButton("Зашифровать на своём секрете")
        self.encrypt_button.clicked.connect(self.encrypt_message)
        layout.addWidget(self.encrypt_button)

        self.decrypt_button = QPushButton("Расшифровать на открытом ключе другого пользователя")
        self.decrypt_button.clicked.connect(self.decrypt_received)
        layout.addWidget(self.decrypt_button)

        self.send_button = QPushButton("Отправить другому пользователю")
        self.send_button.clicked.connect(self.send_to_other)
        layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.public_key = None
        self.private_key = None

    def set_other(self, other):
        self.other: UserWindow = other

    def open_key_dialog(self):
        dialog = KeyGenerationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            p, q, e = dialog.get_values()
            self.generate_rsa_keys(p, q, e)
            self.keys_label.setText(f"Ключи пользователя: ({self.public_key[0]}, {self.public_key[1]})")

    def generate_rsa_keys(self, p, q, e):
        phi = (p - 1) * (q - 1)
        d = mod_inverse(e, phi)
        if d is None or (e * d) % phi != 1:
            raise ValueError("Ошибка генерации ключей")
        self.public_key = (e, p * q)
        self.private_key = (d, p * q)

    def hash_message(self):
        if not self.public_key:
            QMessageBox.critical(self, "Ошибка", "Сначала настройте свои ключи!")
            return

        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.critical(self, "Ошибка", "Введите сообщение для шифрования!")
            return
        
        hashed = hash(message)
        self.hash_input.setText(str(hashed))
    
    def encrypt_message(self):
        if not self.public_key:
            QMessageBox.critical(self, "Ошибка", "Сначала настройте свои ключи!")
            return

        message = self.hash_input.toPlainText()
        if not message:
            QMessageBox.critical(self, "Ошибка", "Получите хэш сообщения")
            return

        encrypted = encrypt_bytes(message, self.private_key)
        self.message_input.setReadOnly(False)
        self.message_input.setText(",".join(map(str, encrypted)))

    def decrypt_received(self):
        try:
            text = self.message_input.toPlainText()
            if not text:
                raise ValueError("Сообщение пустое")
            ciphertext = list(map(int, text.split(",")))
            decrypted = decrypt_bytes(ciphertext, self.other.public_key)
            self.message_input.setText(decrypted)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расшифрования: {str(e)}")

    def receive_encrypted_message(self, encrypted):
        self.message_input.setReadOnly(False)
        self.message_input.setText(encrypted)

    def send_to_other(self):
        encrypted_text = self.message_input.toPlainText()
        self.other.receive_encrypted_message(encrypted_text)

    def get_public_key(self):
        return self.public_key


class DigSignWidget():
    def __init__(self):
        self.alice = UserWindow()
        self.bob = UserWindow()
        self.alice.set_other(self.bob)
        self.bob.set_other(self.alice)

    def show(self):
        self.alice.show()
        self.bob.show()