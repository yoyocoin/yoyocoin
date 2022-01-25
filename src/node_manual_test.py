from sys import argv
from time import sleep

from netp2p import Node


def idle():
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    port = int(argv[1])
    n = Node(None, port=port)
    n.start()
    n._connect()
    idle()


if __name__ == "__main__":
    main()
