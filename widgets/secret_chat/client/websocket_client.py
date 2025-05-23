import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import asyncio
import websockets

from widgets.secret_chat.client.key_generation import KeyGenerationDialog

class WebSocketClient(QThread):
    message_received = pyqtSignal(str)
    key_received = pyqtSignal(str, tuple)

    def __init__(self, username, chat_window):
        super().__init__()
        self.username = username
        self.chat_window = chat_window
        self.websocket = None

    async def connect_and_listen(self):
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            try:
                while True:
                    message = await websocket.recv()
                    if message.startswith("__HELLO__"):
                        _, name, e_str, n_str = message.split(":")
                        other_public_key = (int(e_str), int(n_str))
                        self.key_received.emit(name, other_public_key)
                    else:
                        self.message_received.emit(message)
            except websockets.exceptions.ConnectionClosed:
                pass

    def send_message(self, message):
        asyncio.run(self._send_message_coroutine(message))

    async def _send_message_coroutine(self, message):
        if self.websocket:
            await self.websocket.send(message)

    def run(self):
        asyncio.run(self.connect_and_listen())