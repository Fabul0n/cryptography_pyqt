import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from sympy import isprime as is_prime
from sympy import nextprime

def find_valid_g(p, q):
    while 1:
        g = random.randint(2, p - 2)
        if pow(g, q, p) != 1:
            return g

class DHKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка Диффи-Хеллмана")

        self.p_input = QLineEdit()
        self.g_input = QLineEdit()
        self.a_input = QLineEdit()

        layout = QFormLayout()

        self.generate_pq_button = QPushButton("Сгенерировать p=2q+1")
        self.generate_pq_button.clicked.connect(self.generate_safe_p)

        layout.addRow("Сгенерировать безопасное p", self.generate_pq_button)
        layout.addRow("p:", self.p_input)
        layout.addRow("g:", self.g_input)
        layout.addRow("a (приватный):", self.a_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)

        layout.addRow(self.buttons)
        self.setLayout(layout)

    def generate_safe_p(self):
        """Генерирует простое q, затем проверяет, что p = 2*q + 1 тоже простое"""
        while True:
            q = nextprime(random.randint(10**20, 10**100))
            p = 2 * q + 1
            if is_prime(p):
                self.p_input.setText(str(p))
                self.g_input.setText(str(find_valid_g(p, q)))
                break

    def get_values(self):
        try:
            p = int(self.p_input.text())
            g = int(self.g_input.text())
            a = int(self.a_input.text())
            return p, g, a
        except:
            return None, None, None

    def validate_and_accept(self):
        p, g, a = self.get_values()
        if not p or not g or not a:
            QMessageBox.critical(self, "Ошибка", "Все поля должны быть заполнены числами.")
            return False

        if not is_prime(p):
            QMessageBox.critical(self, "Ошибка", f"Число p = {p} не является простым.")
            return False

        if not ((p - 1) % 2 == 0 and is_prime((p - 1) // 2)):
            QMessageBox.critical(self, "Ошибка", f"p должно быть безопасным простым: p = 2q + 1, где q — тоже простое")
            return False

        q = (p - 1) // 2
        if pow(g, q, p) == 1:
            QMessageBox.critical(self, "Ошибка", f"g = {g} не прошло проверку: g^q mod p == 1")
            return False

        if g <= 1 or g >= p:
            QMessageBox.critical(self, "Ошибка", f"g должно быть в диапазоне: 1 < g < {p}")
            return False

        if a <= 0 or a >= p:
            QMessageBox.critical(self, "Ошибка", f"a должно быть в диапазоне: 0 < a < {p}")
            return False

        self.accept()

class UserWindow(QMainWindow):
    def __init__(self, name="Пользователь"):
        super().__init__()
        self.name = name
        self.setWindowTitle(f"DH - {name}")
        self.setGeometry(700 if name == "Боб" else 100, 100, 500, 400)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.set_params_button = QPushButton("Настроить параметры")
        self.set_params_button.clicked.connect(self.open_key_dialog)
        layout.addWidget(self.set_params_button)

        self.p_label = QLabel("p:")
        self.p_input = QLineEdit()
        self.p_input.setReadOnly(True)
        layout.addWidget(self.p_label)
        layout.addWidget(self.p_input)

        self.g_label = QLabel("g:")
        self.g_input = QLineEdit()
        self.g_input.setReadOnly(True)
        layout.addWidget(self.g_label)
        layout.addWidget(self.g_input)

        self.a_label = QLabel("a:")
        layout.addWidget(self.a_label)

        self.public_key_label = QLabel("Общий ключ:")
        self.public_key_input = QLineEdit()
        self.public_key_input.setReadOnly(True)
        layout.addWidget(self.public_key_label)
        layout.addWidget(self.public_key_input)

        self.message_label = QLabel("Общий публичный ключ другого пользователя:")
        self.partner_public_input = QLineEdit()
        layout.addWidget(self.message_label)
        layout.addWidget(self.partner_public_input)

        self.compute_shared_button = QPushButton("Вычислить общий ключ")
        self.compute_shared_button.clicked.connect(self.compute_shared_key)
        layout.addWidget(self.compute_shared_button)

        self.shared_key_label = QLabel("Секретный ключ: не вычислен")
        self.shared_key_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.shared_key_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.p = None
        self.g = None
        self.a = None
        self.A = None
        self.other = None
        self.s = None

    def set_other(self, other):
        self.other = other

    def open_key_dialog(self):
        dialog = DHKeyDialog(self)
        dialog.show()
        dialog.accepted.connect(lambda: self.handle_dialog_result(dialog))

    def handle_dialog_result(self, dialog):
        if dialog.result() == QDialog.DialogCode.Accepted:
            p, g, a = dialog.get_values()
            self.set_params(p, g, a)
            self.p_input.setText(str(p))
            self.g_input.setText(str(g))
            self.a_label.setText(f"a: {a}")
            self.A = pow(g, a, p)
            self.public_key_input.setText(f"{self.A}")

    def set_params(self, p, g, a):
        self.p = p
        self.g = g
        self.a = a
        self.A = pow(g, a, p)

    def compute_shared_key(self):
        if self.p is None or self.A is None:
            QMessageBox.critical(self, "Ошибка", "Сначала настройте свои параметры!")
            return

        partner_A_text = self.partner_public_input.text().strip()
        if not partner_A_text.isdigit():
            QMessageBox.critical(self, "Ошибка", "Введите корректный публичный ключ другого пользователя!")
            return

        partner_A = int(partner_A_text)
        self.s = pow(partner_A, self.a, self.p)
        self.shared_key_label.setText(f"Секретный ключ: {self.s}")

    def get_public_key(self):
        return self.A


class DiffieHellman:
    def __init__(self):
        self.alice = UserWindow("Алиса")
        self.bob = UserWindow("Боб")
        self.alice.set_other(self.bob)
        self.bob.set_other(self.alice)

    def show(self):
        self.alice.show()
        self.bob.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dh_app = DiffieHellman()
    dh_app.show()

    sys.exit(app.exec())