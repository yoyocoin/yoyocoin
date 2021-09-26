from sys import argv
from time import sleep

from network.node import Node
from network.config import Config


def idle():
    while True:
        sleep(1)


def main():
    ip = argv[1]
    Config.node_listen_host = ip
    n = Node(on_network_broadcast=lambda x: print("broadcast", x))
    n.start()
    idle()

if __name__ == "__main__":
    main()
