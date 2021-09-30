from ..protocol import Protocol
from ..message import Message
from ..config import Config


class VersionProtocol(Protocol):
    name = "version_protocol"

    def handle(self, sender, message):
        try:
            connection = self.node.get_connection(sender)
        except KeyError:
            return
        connection.version = message.dict_message["version"]

    @classmethod
    def create_version_message(cls):
        return Message(dict_message={"protocol": cls.name, "version": Config.node_version})
