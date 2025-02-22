import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QTextEdit,
)
from widgets.atbash import AtbashWidget

class CipherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шифрование")
        self.setGeometry(100, 100, 400, 300)

        main_widget = QWidget()
        layout = QVBoxLayout()

        self.cipher_label = QLabel("Выберите шифр:")
        layout.addWidget(self.cipher_label)

        self.cipher_combo = QComboBox()
        self.cipher_combo.addItem("Атбаш")
        layout.addWidget(self.cipher_combo)

        self.select_button = QPushButton("Выбрать")
        self.select_button.clicked.connect(self.show_cipher_window)
        layout.addWidget(self.select_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def show_cipher_window(self):
        cipher_name = self.cipher_combo.currentText()

        if cipher_name == "Атбаш":
            self.cipher_window = AtbashWidget()

        self.cipher_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CipherApp()
    window.show()
    sys.exit(app.exec())