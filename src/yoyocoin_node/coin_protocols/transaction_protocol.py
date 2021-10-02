"""
Protocol that handle transaction broadcast
1. deserialize data
2. add to chain
3. broadcast forward
"""

from p2p_network.protocol import Protocol
from p2p_network.message import Message
from blockchain import Chain


class TransactionProtocol(Protocol):
    name = "transactions"

    def __init__(self, node, blockchain: Chain):
        super().__init__(node)
        self.blockchain = blockchain

    def handle(self, sender, message):
        """
        Handle incoming message
        :param sender: address of sending node (can be used to get connection object)
        :param message: message object sent to you
        :return: None
        """
        if message.dict_message.get("action", None) == "new-transaction":
            transaction_dict = message.dict_message["transaction"]
            self.blockchain.add_transaction(transaction_dict)
            self._broadcast_forward(message, sender)

    def _broadcast_forward(self, message, sender):
        self.node.broadcast(message, exclude=[sender])

    @classmethod
    def create_broadcast_transaction_message(cls, transaction_dict: dict) -> Message:
        return Message(
            dict_message={"protocol": cls.name, "action": "new-transaction", "transaction": transaction_dict},
            broadcast=True,
        )
