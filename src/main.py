from time import sleep
from network.node import Node


def idle():
    while True:
        sleep(1)


def main():
    n = Node(on_network_broadcast=lambda x: print("broadcast", x))
    n.start()
    idle()

if __name__ == "__main__":
    main()
