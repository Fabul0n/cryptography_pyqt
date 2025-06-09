from PyQt6.QtWidgets import QApplication
import sys
from qasync import QEventLoop
import asyncio
from secret_chat.client.login_widget import LoginWidget
from secret_chat.client.chat_widget import ChatWidget
from secret_chat.server.server_gui import ServerGUI


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    server = ServerGUI()
    server.show()

    login_widget = LoginWidget()
    login_widget2 = LoginWidget()
    
    def on_login_success(username):
        chat_widget = ChatWidget(username, loop)
        chat_widget.show()
    
    login_widget.login_successful.connect(on_login_success)
    login_widget.show()
    login_widget2.login_successful.connect(on_login_success)
    login_widget2.show()


    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()