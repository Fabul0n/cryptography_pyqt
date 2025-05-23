import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import asyncio
import websockets
from sympy import isprime as is_prime
from sympy import nextprime
from math import gcd

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