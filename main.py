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
    QHBoxLayout,
    QFrame
)
from widgets.atbash import AtbashWidget
from widgets.caesar import CaesarWidget
from widgets.richelieu import RichelieuWidget
from widgets.gronsfeld import GronsfelduWidget
from widgets.vigenere import VigenereWidget
from widgets.playfair import PlayfairWidget
from widgets.frequency_analyser import FrequencyAnalyzerWidget
from widgets.gamma import GammaWidget
from widgets.des import DESWidget
from widgets.RSA import RSAWidget
from widgets.keyXchange import DiffieHellman
from widgets.digital_sign import DigSignWidget
from widgets.secret_chat.client.client_widget import ClientWidget
from widgets.secret_chat.server.server import ServerGUI

import random



class CipherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шифрование")
        self.setGeometry(100, 100, 400, 300)

        main_widget = QWidget()
        layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.cipher_label = QLabel("Выберите шифр:")
        v_layout.addWidget(self.cipher_label)

        self.cipher_combo = QComboBox()
        self.cipher_combo.addItem("Атбаш")
        self.cipher_combo.addItem("Цезарь")
        self.cipher_combo.addItem("Ришелье")
        self.cipher_combo.addItem("Гронсфельд")
        self.cipher_combo.addItem("Виженер")
        self.cipher_combo.addItem("Плейфер")
        self.cipher_combo.addItem("Частотный анализатор")
        self.cipher_combo.addItem("Гаммирование")
        self.cipher_combo.addItem("DES")
        self.cipher_combo.addItem("RSA")
        self.cipher_combo.addItem("Диффи-Хеллман")
        self.cipher_combo.addItem("Цифровая подпись")
        v_layout.addWidget(self.cipher_combo)

        self.select_button = QPushButton("Выбрать")
        self.select_button.clicked.connect(self.show_cipher_window)
        v_layout.addWidget(self.select_button)

        layout.addLayout(v_layout)


        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)


        v_layout2 = QVBoxLayout()

        v_layout2.addWidget(QLabel("Секретный чат:"))

        self.secret_chat_client_button = QPushButton("Клиент")
        self.secret_chat_client_button.clicked.connect(self.secret_chat_client)
        v_layout2.addWidget(self.secret_chat_client_button)

        self.secret_chat_server_button = QPushButton("Сервер")
        self.secret_chat_server_button.clicked.connect(self.secret_chat_server)
        v_layout2.addWidget(self.secret_chat_server_button)

        layout.addLayout(v_layout2)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def secret_chat_client(self):
        self.secret_chat_cli = ClientWidget()
        self.close()

    def secret_chat_server(self):
        self.secret_chat_srvr = ServerGUI()
        self.secret_chat_srvr.show()
        self.close()

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
            case 'Частотный анализатор':
                self.cipher_widget = FrequencyAnalyzerWidget()
            case 'Гаммирование':
                self.cipher_widget = GammaWidget()
            case 'DES':
                self.cipher_widget = DESWidget()
            case 'RSA':
                self.cipher_widget = RSAWidget()
            case 'Диффи-Хеллман':
                self.cipher_widget = DiffieHellman()
            case 'Цифровая подпись':
                self.cipher_widget = DigSignWidget()
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