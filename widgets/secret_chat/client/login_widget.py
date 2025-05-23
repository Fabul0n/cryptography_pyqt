import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import asyncio
import websockets

from widgets.secret_chat.client.key_generation import KeyGenerationDialog


class LoginWidget(QWidget):
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в чат")
        self.resize(300, 100)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Введите ваше имя:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.connect_button = QPushButton("Подключиться к серверу")
        self.connect_button.clicked.connect(self.on_login)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def on_login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя!")
            return
        self.login_successful.emit(name)
        self.close()