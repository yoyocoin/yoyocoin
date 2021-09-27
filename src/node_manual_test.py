from sys import argv
from time import sleep

from yoyocoin_node import YoyocoinNode


def idle():
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    ip = argv[1]
    n = YoyocoinNode(host=ip)
    n.start()
    sleep(20)
    if n.node.connected_peers:
        print(n.node.connected_peers)
        connection = n.node.get_connection(n.node.connected_peers[0])
        connection.send(f"hello from {ip}".encode())
    idle()


if __name__ == "__main__":
    main()
