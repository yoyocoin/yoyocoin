import socket


__all__ = ["TimeoutException", "InvalidMessageFormat", "ConnectionClosed"]


class TimeoutException(socket.timeout, TimeoutError):
    pass


class InvalidMessageFormat(ValueError):
    pass


class ConnectionClosed(ConnectionError):
    pass
