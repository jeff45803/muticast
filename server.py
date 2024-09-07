import socket
import struct
import time

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 设置多播TTL（时间存活数）
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


while True:
    message = 'This is the message'.encode('utf-8')
    # 发送消息到多播组
    sock.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))
    print('Message sent!')
    time.sleep(1)

sock.close()
