import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QPushButton, QFileDialog, QMessageBox)
from ciphers.gamma import Gamma

class GammaWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gamma Cipher Widget")
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.text_edit = QTextEdit()
        
        self.encrypt_btn = QPushButton("Зашифровать")
        self.decrypt_btn = QPushButton("Расшифровать")
        self.load_btn = QPushButton("Загрузить из файла")
        self.save_btn = QPushButton("Сохранить в файл")
        
        layout.addWidget(self.text_edit)
        layout.addWidget(self.encrypt_btn)
        layout.addWidget(self.decrypt_btn)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.save_btn)
        
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.decrypt_btn.clicked.connect(self.decrypt)
        self.load_btn.clicked.connect(self.load_file)
        self.save_btn.clicked.connect(self.save_file)

    def encrypt(self):
        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для шифрования")
            return
            
        cipher = Gamma(text)
        encrypted = cipher.encode()
        self.text_edit.setText(encrypted)

    def decrypt(self):
        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для расшифрования")
            return
            
        try:
            cipher = Gamma(text)
            decrypted = cipher.decode()
            try:
                self.text_edit.setText(decrypted.decode('utf-8'))
            except UnicodeDecodeError:
                self.text_edit.setText(decrypted.hex())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат зашифрованного текста")

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Все файлы (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'rb') as f:
                    data = f.read()
                self.text_edit.setText(data.hex())
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_file(self):
        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Все файлы (*.*)"
        )
        if file_name:
            try:
                data = bytes.fromhex(text)
                with open(file_name, 'wb') as f:
                    f.write(data)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = GammaWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()