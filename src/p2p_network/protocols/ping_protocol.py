from collections import defaultdict
from time import time

from loguru import logger

from ..message import Message
from ..protocol import Protocol


PING_TIMEOUT = 90


class PingProtocol(Protocol):
    name = "ping"

    def __init__(self, node):
        super().__init__(node, require_heartbeat=True, heartbeat_interval=60)
        self.connections_status = defaultdict(dict)

    def handle(self, sender, message):
        status = self.connections_status[sender]
        status["last_ping"] = time()

    def heartbeat(self):
        super().heartbeat()
        for adderss in self.node.connected_peers:
            connection = self.node.get_connection(adderss)
            status = self.connections_status[adderss]
            if status.get("last_ping", None) and time() - status["last_ping"] > PING_TIMEOUT:
                connection.close()
                logger.debug(f"Ping timeout, closing connection {adderss}.")
            else:
                connection.send(self.create_ping_message().to_bytes())

    @classmethod
    def create_ping_message(cls):
        return Message(dict_message={"protocol": cls.name})
