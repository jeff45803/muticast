import socket
def multicast_server(multicast_group, multicast_port=5007):
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(3)  # 设置超时时间为 10 秒
    # 启用发送多播选项
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    try:
        while True:
            # 让用户输入要发送的消息
            message = input(f"Enter message to send to {multicast_group}: ").strip()
            if not message:
                print("Message cannot be empty. Please enter a valid message.")
                continue

            # 发送消息到多播组
            sock.sendto(message.encode('utf-8'), (multicast_group, multicast_port))
            print(f"Sent message: {message}")

    except KeyboardInterrupt:
        print("Server interrupted.")
    finally:
        sock.close()


if __name__ == "__main__":
    # 输入多播组
    group = input("Enter multicast group to send to (e.g., 224.1.1.1): ").strip()
    multicast_server(group)
