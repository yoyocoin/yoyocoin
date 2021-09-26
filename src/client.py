from time import sleep
from network.connection import Connection  # type: ignore


def main():
    connection = Connection.connect(address=("127.0.0.2", 6001), recv_queue=None)
    connection.send(b"hello it is working")
    sleep(5)
    connection.close()


if __name__ == "__main__":
    main()
