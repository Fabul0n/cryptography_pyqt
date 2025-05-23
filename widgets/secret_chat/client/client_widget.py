import sys
from PyQt6.QtWidgets import QApplication, QWidget

from widgets.secret_chat.client.login_widget import LoginWidget
from widgets.secret_chat.client.chat_widget import ChatWidget


class ClientWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.login_widget = LoginWidget()
        self.login_widget.login_successful.connect(self.show_chat_window)
        self.login_widget.show()

    def show_chat_window(self, username):
        self.chat_widget = ChatWidget(username)
        self.chat_widget.show()