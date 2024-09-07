import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import socket
import threading

class MulticastServerUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.sock = None
        self.listener_thread = None

    def initUI(self):
        layout = QVBoxLayout()

        # Multicast Group Input
        self.groupLabel = QLabel("Enter multicast group (e.g., 224.1.1.1):")
        self.groupInput = QLineEdit(self)
        layout.addWidget(self.groupLabel)
        layout.addWidget(self.groupInput)

        # Message Input
        self.messageLabel = QLabel("Enter message to send:")
        self.messageInput = QTextEdit(self)
        layout.addWidget(self.messageLabel)
        layout.addWidget(self.messageInput)

        # Send Button
        self.sendButton = QPushButton("Send Message", self)
        self.sendButton.clicked.connect(self.send_message)
        layout.addWidget(self.sendButton)

        # Message Display for receiving client messages
        self.messageDisplay = QTextEdit(self)
        self.messageDisplay.setReadOnly(True)
        layout.addWidget(self.messageDisplay)

        # Setting layout
        self.setLayout(layout)
        self.setWindowTitle("Multicast Server")

    def send_message(self):
        multicast_group = self.groupInput.text()
        message = self.messageInput.toPlainText()

        if not multicast_group or not message:
            print("Multicast group or message is empty.")
            return

        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        try:
            self.sock.sendto(message.encode('utf-8'), (multicast_group, 5007))
            print(f"Sent message: {message} to group: {multicast_group}")
            self.messageDisplay.append(f"Sent message: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

        self.messageInput.clear()

        if self.listener_thread is None:
            self.listener_thread = threading.Thread(target=self.listen, daemon=True)
            self.listener_thread.start()

    def listen(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', 5007))

        while True:
            try:
                data, address = self.sock.recvfrom(1024)
                message = data.decode('utf-8')

                if ": " in message:
                    sender_name, message_content = message.split(": ", 1)
                    self.messageDisplay.append(f"Received message from {sender_name}: {message_content}")
                    self.messageDisplay.append("Received message")  # Indicate reply received
                else:
                    self.messageDisplay.append(f"Received message: {message} from {address}")

            except Exception as e:
                self.messageDisplay.append(f"Error receiving message: {e}")
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    serverUI = MulticastServerUI()
    serverUI.show()
    sys.exit(app.exec_())
