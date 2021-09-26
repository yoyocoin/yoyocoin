import socket


class TimeoutException(socket.timeout, TimeoutError):
    pass
