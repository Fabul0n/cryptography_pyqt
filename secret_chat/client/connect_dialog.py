from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox


class ConnectToUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подключение к пользователю")

        self.name_input = QLineEdit()

        layout = QFormLayout()
        layout.addRow("Введите имя пользователя:", self.name_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        self.setLayout(layout)

    def get_target_name(self):
        return self.name_input.text().strip()

    def validate_and_accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Ошибка", "Введите имя пользователя.")
            return
        self.accept()