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
        self.joined_groups = {}  # 使用字典存储已加入的多播组

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

        # Message Input for sending back to the server
        self.sendLabel = QLabel("Enter message to send:")
        self.sendInput = QLineEdit(self)
        layout.addWidget(self.sendLabel)
        layout.addWidget(self.sendInput)

        # Send Button
        self.sendButton = QPushButton("Send Message", self)
        self.sendButton.clicked.connect(self.send_message)
        layout.addWidget(self.sendButton)

        # Setting layout
        self.setLayout(layout)
        self.setWindowTitle("Multicast Client")

    def join_group(self):
        name = self.nameInput.text()
        multicast_group = self.groupInput.text()

        if not name or not multicast_group:
            self.messageDisplay.append("Name or multicast group is empty.")
            return

        if self.sock is None:
            # 创建UDP套接字
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', 5007))

        if multicast_group not in self.joined_groups:
            # 加入新的多播组
            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            # 将多播组加入到字典中
            self.joined_groups[multicast_group] = mreq
            self.messageDisplay.append(f"{name} joined multicast group {multicast_group}")

            # 如果是第一次加入多播组，启动监听线程
            if len(self.joined_groups) == 1:
                self.listener_thread = threading.Thread(target=self.listen, daemon=True)
                self.listener_thread.start()
        else:
            self.messageDisplay.append(f"Already joined multicast group {multicast_group}")

    def leave_group(self):
        multicast_group = self.groupInput.text()

        if multicast_group in self.joined_groups:
            # 退出多播组
            mreq = self.joined_groups[multicast_group]
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            del self.joined_groups[multicast_group]  # 从字典中删除组播组
            self.messageDisplay.append(f"Left multicast group {multicast_group}")
        else:
            self.messageDisplay.append(f"Not a member of multicast group {multicast_group}")

    def listen(self):
        while self.joined_groups:
            try:
                data, address = self.sock.recvfrom(1024)
                message = data.decode('utf-8')
                self.messageDisplay.append(f"Received message: {message} from {address}")

                # Store the server address for reply
                self.server_address = address

            except socket.error as e:
                self.messageDisplay.append(f"Socket error: {e}")
                break

    def send_message(self):
        message = self.sendInput.text()
        name = self.nameInput.text()

        if not message or not name:
            self.messageDisplay.append("Message or name is empty.")
            return

        # 格式化消息为 'name: message'
        formatted_message = f"{name}: {message}"

        # 向服务器地址发送消息
        if self.sock is not None and hasattr(self, 'server_address'):
            try:
                self.sock.sendto(formatted_message.encode('utf-8'), self.server_address)
                self.messageDisplay.append(f"Sent message to server: {formatted_message}")
                self.sendInput.clear()
            except socket.error as e:
                self.messageDisplay.append(f"Failed to send message: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    clientUI = MulticastClientUI()
    clientUI.show()
    sys.exit(app.exec_())
