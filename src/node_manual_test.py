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
    idle()


if __name__ == "__main__":
    main()
