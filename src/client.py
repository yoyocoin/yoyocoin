from time import sleep
from network.connection import Connection


def main():
    connection = Connection.connect(address=("localhost", 6001), recv_queue=None)
    connection.send(b"hello it is working")
    sleep(20)
    connection.close()

if __name__ == "__main__":
    main()
