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
from widgets.caesar import CaesarWidget
from widgets.richelieu import RichelieuWidget
from widgets.gronsfeld import GronsfelduWidget
from widgets.vigenere import VigenereWidget
from widgets.playfair import PlayfairWidget

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
        self.cipher_combo.addItem("Цезарь")
        self.cipher_combo.addItem("Ришелье")
        self.cipher_combo.addItem("Гронсфельд")
        self.cipher_combo.addItem("Виженер")
        self.cipher_combo.addItem("Плейфер")
        layout.addWidget(self.cipher_combo)

        self.select_button = QPushButton("Выбрать")
        self.select_button.clicked.connect(self.show_cipher_window)
        layout.addWidget(self.select_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def show_cipher_window(self):
        cipher_name = self.cipher_combo.currentText()

        match cipher_name:
            case 'Атбаш':
                self.cipher_widget = AtbashWidget()
            case 'Цезарь':
                self.cipher_widget = CaesarWidget()
            case 'Ришелье':
                self.cipher_widget = RichelieuWidget()
            case 'Гронсфельд':
                self.cipher_widget = GronsfelduWidget()
            case 'Виженер':
                self.cipher_widget = VigenereWidget()
            case 'Плейфер':
                self.cipher_widget = PlayfairWidget()
            case _:
                e = Exception()
                e.add_note('Error in cipher name')
                raise e
        

        self.cipher_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CipherApp()
    window.show()
    sys.exit(app.exec())