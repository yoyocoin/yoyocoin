from typing import Union
import random

from ..protocol import Protocol
from ..message import Message


class BootstrapProtocol(Protocol):
    SEND_MY_ADDRESS_INTERVAL = 60
    name: str = "bootstrap"

    def __init__(self, node):
        super().__init__(node, require_heartbeat=True, heartbeat_interval=self.SEND_MY_ADDRESS_INTERVAL)

    def _add_active_node_address(self, address: Union[list, None]):
        if address is None:
            return
        tuple_address = tuple(address)
        self.node.peer_list.add(tuple_address)
        if len(self.node.peer_list) > 20000:
            self.node.peer_list.pop()

    def _handle_active_nodes_request(self, sender, limit):
        connection = self.node.get_connection(sender)
        random_peers = random.sample(self.node.peer_list, k=min(limit, len(self.node.peer_list)))
        connection.send(Message({"peers": random_peers}).to_bytes())

    def handle(self, sender, message: Message):
        action = message.dict_message.get("action", None)
        if action == "active_nodes_list":
            self._handle_active_nodes_request(sender, message.dict_message.get("limit"))
        elif action == "active_node_address":
            self._add_active_node_address(message.dict_message.get("address", None))
            message.dict_message['address'] = tuple(message.dict_message['address'])
            self.node.broadcast(message, exclude=[sender])  # relay

    def heartbeat(self):
        super().heartbeat()
        self.node.broadcast(self.create_active_node_address_message(self.node.my_address))

    @classmethod
    def create_active_node_address_message(cls, address) -> Message:
        return Message(
            {"protocol": cls.name, "action": "active_node_address", "address": address},
            broadcast=True,
        )

    @classmethod
    def create_active_nodes_list_message(cls, limit) -> Message:
        return Message({"protocol": cls.name, "action": "active_nodes_list", "limit": limit})
