from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QDialogButtonBox, QMessageBox
)
from sympy import randprime, isprime, primitive_root


class DHParamsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка Диффи-Хеллмана")

        self.p_input = QLineEdit()
        self.g_input = QLineEdit()
        self.r_input = QLineEdit()

        layout = QFormLayout()

        self.generate_pq_button = QPushButton("Сгенерировать p=2q+1")
        self.generate_pq_button.clicked.connect(self.generate_safe_p)

        layout.addRow("Сгенерировать безопасное p", self.generate_pq_button)
        layout.addRow("p:", self.p_input)
        layout.addRow("g:", self.g_input)
        layout.addRow("a (секретный ключ):", self.r_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        self.setLayout(layout)

    def generate_safe_p(self):
        while True:
            q = randprime(10**29, 10**30)
            p = 2 * q + 1
            if isprime(p):
                g = primitive_root(p)
                r = randprime(2**2047, 2**2048)
                self.p_input.setText(str(p))
                self.g_input.setText(str(g))
                self.r_input.setText(str(r))
                break

    def get_values(self):
        try:
            p = int(self.p_input.text())
            g = int(self.g_input.text())
            a = int(self.r_input.text())
            return p, g, a
        except:
            return None, None, None

    def validate_and_accept(self):
        p, g, a = self.get_values()

        if not p or not g or not a:
            QMessageBox.critical(self, "Ошибка", "Все поля должны быть заполнены числами.")
            return False

        if not isprime(p):
            QMessageBox.critical(self, "Ошибка", f"Число p = {p} не является простым.")
            return False

        if not ((p - 1) % 2 == 0 and isprime((p - 1) // 2)):
            QMessageBox.critical(self, "Ошибка",
                                 f"p должно быть безопасным: p = 2q + 1, где q тоже простое")
            return False

        q = (p - 1) // 2
        if pow(g, q, p) == 1:
            QMessageBox.critical(self, "Ошибка", f"g = {g} не прошло проверку: g^q mod p != 1")
            return False

        if g <= 1 or g >= p:
            QMessageBox.critical(self, "Ошибка", f"g должно быть в диапазоне: 1 < g < {p}")
            return False

        if a < 2**2047 or a >= 2**2048:
            QMessageBox.critical(self, "Ошибка", f"a вне допустимого диапазона")
            return False

        self.accept()