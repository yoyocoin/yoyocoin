import socket


__all__ = ["TimeoutException", "InvalidMessageFormat", "ConnectionClosed"]


TimeoutException = (socket.timeout, TimeoutError)


class InvalidMessageFormat(ValueError):
    pass


class ConnectionClosed(ConnectionError):
    pass
