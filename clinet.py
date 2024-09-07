import socket
import struct

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 允许socket重用地址
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定到多播组的端口
sock.bind(('', MULTICAST_PORT))

# 加入多播组
group = socket.inet_aton(MULTICAST_GROUP)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# 接收来自多播组的消息

while True:
    data, address = sock.recvfrom(1024)
    print(f"Received message: {data.decode('utf-8')} from {address}")

sock.close()