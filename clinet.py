import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import socket
import struct
import threading

class MulticastClientUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.sock = None
        self.joined_group = None

    def initUI(self):
        layout = QVBoxLayout()

        # Name Input
        self.nameLabel = QLabel("Enter your name:")
        self.nameInput = QLineEdit(self)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.nameInput)

        # Multicast Group Input
        self.groupLabel = QLabel("Enter multicast group (e.g., 224.1.1.1):")
        self.groupInput = QLineEdit(self)
        layout.addWidget(self.groupLabel)
        layout.addWidget(self.groupInput)

        # Join/Leave Buttons
        self.joinButton = QPushButton("Join Group", self)
        self.joinButton.clicked.connect(self.join_group)
        layout.addWidget(self.joinButton)

        self.leaveButton = QPushButton("Leave Group", self)
        self.leaveButton.clicked.connect(self.leave_group)
        layout.addWidget(self.leaveButton)

        # Message Display
        self.messageDisplay = QTextEdit(self)
        self.messageDisplay.setReadOnly(True)
        layout.addWidget(self.messageDisplay)

        # Setting layout
        self.setLayout(layout)
        self.setWindowTitle("Multicast Client")

    def join_group(self):
        name = self.nameInput.text()
        multicast_group = self.groupInput.text()

        if not name or not multicast_group:
            self.messageDisplay.append("Name or multicast group is empty.")
            return

        # Create or reuse the socket
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', 5007))

        # Join multicast group
        if self.joined_group is None:
            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            self.joined_group = multicast_group
            self.messageDisplay.append(f"{name} joined multicast group {multicast_group}")

            # Start listening for messages
            self.listener_thread = threading.Thread(target=self.listen, daemon=True)
            self.listener_thread.start()

    def leave_group(self):
        if self.joined_group:
            group = socket.inet_aton(self.joined_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            self.messageDisplay.append(f"Left multicast group {self.joined_group}")
            self.joined_group = None

    def listen(self):
        while self.joined_group:
            try:
                data, address = self.sock.recvfrom(1024)
                self.messageDisplay.append(f"Received message: {data.decode('utf-8')} from {address}")
            except socket.error as e:
                self.messageDisplay.append(f"Socket error: {e}")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    clientUI = MulticastClientUI()
    clientUI.show()
    sys.exit(app.exec_())
