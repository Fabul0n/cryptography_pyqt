from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal


class LoginWidget(QWidget):
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в чат")
        self.resize(300, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите ваше имя:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.connect_button = QPushButton("Продолжить")
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