import socket


__all__ = ["TimeoutException", "ConnectionClosed"]


TimeoutException = (socket.timeout, TimeoutError)


class ConnectionClosed(ConnectionError):
    pass
