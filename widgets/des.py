import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QTextEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QLabel, QDialog, QLineEdit,
                            QHBoxLayout)
from ciphers.des import encode, decode, generate_des_key

class LCGSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки Линейного Конгруэнтного Генератора")
        self.resize(400, 200)

        main_layout = QVBoxLayout()

        self.seedLabel = QLabel("Начальное значение (зерно):", self)
        main_layout.addWidget(self.seedLabel)

        self.seedEdit = QLineEdit(self)
        main_layout.addWidget(self.seedEdit)

        self.aLabel = QLabel("Множитель (a):", self)
        main_layout.addWidget(self.aLabel)

        self.aEdit = QLineEdit(self)
        main_layout.addWidget(self.aEdit)

        self.cLabel = QLabel("Слагаемое (c):", self)
        main_layout.addWidget(self.cLabel)

        self.cEdit = QLineEdit(self)
        main_layout.addWidget(self.cEdit)

        self.mLabel = QLabel("Модуль (m):", self)
        main_layout.addWidget(self.mLabel)

        self.mEdit = QLineEdit(self)
        main_layout.addWidget(self.mEdit)

        button_layout = QHBoxLayout()

        button_layout.addStretch(1)

        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        button_layout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Отмена", self)
        self.cancelButton.clicked.connect(self.reject)
        button_layout.addWidget(self.cancelButton)

        button_layout.addStretch(1)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_settings(self):
        seed = int(self.seedEdit.text())
        a = int(self.aEdit.text())
        c = int(self.cEdit.text())
        m = int(self.mEdit.text())
        return seed, a, c, m

class DESWidget(QMainWindow):
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
        
        self.conf_gen = QPushButton("Редактировать конфиг")
        layout.addWidget(self.conf_gen)
        layout.addWidget(self.text_edit)
        self.language_combo = QComboBox()
        self.language_combo.addItems(['', 'Файл', 'Ввод'])
        layout.addWidget(QLabel('Выберите режим:'))
        layout.addWidget(self.language_combo)
        layout.addWidget(self.encrypt_btn)
        layout.addWidget(self.decrypt_btn)
        layout.addWidget(self.load_btn)
        layout.addWidget(self.save_btn)
        self.seed = 2281337
        self.a = 1103515245
        self.c = 12345
        self.m = 2**64
        
        self.conf_gen.clicked.connect(self.configure_lcg)
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.decrypt_btn.clicked.connect(self.decrypt)
        self.load_btn.clicked.connect(self.load_file)
        self.save_btn.clicked.connect(self.save_file)
        self.file_text = None

    def configure_lcg(self):
        dialog = LCGSettingsDialog(self)
        dialog.seedEdit.setText(str(self.seed))
        dialog.aEdit.setText(str(self.a))
        dialog.cEdit.setText(str(self.c))
        dialog.mEdit.setText(str(self.m))

        if dialog.exec():
            self.seed, self.a, self.c, self.m = dialog.get_settings()

    def encrypt(self):
        mode = self.language_combo.currentText()
        if not mode:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите режим!')
            return
        if mode == 'Ввод':
            text = self.text_edit.toPlainText()
        else:
            text = self.file_text
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для шифрования")
            return
            
        key = generate_des_key(self.seed, self.a, self.c, self.m)
        encrypted = encode(text, key)
        self.file_text = encrypted
        if mode == 'Ввод':
            self.text_edit.setText(encrypted)
        else:
            self.text_edit.setText('Файл зашифрован')

    def decrypt(self):
        mode = self.language_combo.currentText()
        if not mode:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите режим!')
            return
        if mode == 'Ввод':
            text = self.text_edit.toPlainText()
        else:
            text = self.file_text
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для расшифрования")
            return
            
        try:
            key = generate_des_key(self.seed, self.a, self.c, self.m)
            decrypted = decode(text, key)
            self.file_text = decrypted
            if mode == 'Ввод':
                try:
                    self.text_edit.setText(decrypted.decode('utf-8'))
                except UnicodeDecodeError:
                    self.text_edit.setText(decrypted.hex())
            else:
                self.text_edit.setText('Файл расшифрован')
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат зашифрованного текста")
            raise

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Все файлы (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'rb') as f:
                    data = f.read()
                self.file_text = data
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def save_file(self):
        text = self.file_text
        if not text:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Все файлы (*.*)"
        )
        if file_name:
            try:
                data = text
                with open(file_name, 'wb') as f:
                    f.write(data)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = DESWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()