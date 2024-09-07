import socket
import struct
import threading

class MulticastClient:
    def __init__(self, name, multicast_port=5007):
        self.name = name
        self.multicast_port = multicast_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.multicast_port))
        self.joined_groups = {}

    def join_group(self, multicast_group):
        if multicast_group not in self.joined_groups:
            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            self.joined_groups[multicast_group] = True
            print(f"{self.name} joined multicast group {multicast_group}")
        else:
            print(f"{self.name} is already in multicast group {multicast_group}")

    def leave_group(self, multicast_group):
        if multicast_group in self.joined_groups:
            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            del self.joined_groups[multicast_group]
            print(f"{self.name} left multicast group {multicast_group}")
        else:
            print(f"{self.name} is not in multicast group {multicast_group}")

    def listen(self):
        while True:
            try:
                data, address = self.sock.recvfrom(1024)
                print(f"{self.name} received message: {data.decode('utf-8')} from {address}")
            except socket.error as e:
                print(f"Socket error: {e}")
                break

def manage_client(client):
    # 启动监听线程
    listener_thread = threading.Thread(target=client.listen, daemon=True)
    listener_thread.start()

    try:
        while True:
            command = input("Enter command (new <group>, leave <group>, exit): ").strip().lower()
            if command.startswith('new'):
                _, multicast_group = command.split()
                client.join_group(multicast_group)
            elif command.startswith('leave'):
                _, multicast_group = command.split()
                client.leave_group(multicast_group)
            elif command == 'exit':
                for group in list(client.joined_groups.keys()):
                    client.leave_group(group)
                break
    except KeyboardInterrupt:
        print("Client interrupted.")
    finally:
        client.sock.close()

if __name__ == "__main__":
    name = input("Enter your name: ").strip()
    client = MulticastClient(name)
    manage_client(client)
