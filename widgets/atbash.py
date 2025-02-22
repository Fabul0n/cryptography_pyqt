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
from ciphers.atbash import Atbash

class AtbashWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шифр Атбаш")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.input_label = QLabel("Введите текст для шифровки/расшифровки:")
        layout.addWidget(self.input_label)

        self.text_input = QTextEdit()
        layout.addWidget(self.text_input)

        self.encrypt_button = QPushButton("Зашифровать")
        self.encrypt_button.clicked.connect(self._process_encryption)
        layout.addWidget(self.encrypt_button)

        self.decrypt_button = QPushButton("Расшифровать")
        self.decrypt_button.clicked.connect(self._process_decryption)
        layout.addWidget(self.decrypt_button)

        self.result_label = QLabel("Результат:")
        layout.addWidget(self.result_label)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.setLayout(layout)

    def _process_encryption(self):
        input_text = self.text_input.toPlainText()
        result = self._encrypt_text(input_text)
        self.result_output.setText(result)

    def _process_decryption(self):
        input_text = self.text_input.toPlainText()
        result = self._decrypt_text(input_text)
        self.result_output.setText(result)

    @staticmethod
    def _encrypt_text(text):
        encoder = Atbash(text)
        return encoder.encode()
    
    @staticmethod
    def _decrypt_text(text):
        decoder = Atbash(text)
        return decoder.decode()