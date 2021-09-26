from sys import argv
from time import sleep

from network.node import Node  # type: ignore
from network.config import Config  # type: ignore


def idle():
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    ip = argv[1]
    Config.node_listen_host = ip
    n = Node(on_network_broadcast=lambda x: print("broadcast", x))
    n.start()
    idle()


if __name__ == "__main__":
    main()
