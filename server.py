import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import socket

class MulticastServerUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.sock = None

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

        # Setting layout
        self.setLayout(layout)
        self.setWindowTitle("Multicast Server")

    def send_message(self):
        multicast_group = self.groupInput.text()
        message = self.messageInput.toPlainText()

        if not multicast_group or not message:
            print("Multicast group or message is empty.")
            return

        # Create or reuse the socket
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # Send the message
        try:
            self.sock.sendto(message.encode('utf-8'), (multicast_group, 5007))
            print(f"Sent message: {message} to group: {multicast_group}")
        except Exception as e:
            print(f"Error sending message: {e}")

        # Clear the input for the next message
        self.messageInput.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    serverUI = MulticastServerUI()
    serverUI.show()
    sys.exit(app.exec_())
