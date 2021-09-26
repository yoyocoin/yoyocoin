from sys import argv
from time import sleep

from p2p_network.node import Node  # type: ignore
from p2p_network.config import Config  # type: ignore


def idle():
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    ip = argv[1]
    Config.node_listen_host = ip
    n = Node(on_message=lambda x: print("broadcast", x))
    n.start()
    sleep(20)
    if n.connected_peers:
        print(n.connected_peers)
        connection = n.get_connection(n.connected_peers[0])
        connection.send(f"hello from {ip}".encode())
    idle()


if __name__ == "__main__":
    main()
