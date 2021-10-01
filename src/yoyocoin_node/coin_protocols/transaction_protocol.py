"""
Protocol that handle transaction broadcast
1. deserialize data
2. add to chain
3. broadcast forward
"""

from p2p_network.protocol import Protocol


class TransactionProtocol(Protocol):
    name = "transactions"

    def __init__(self, node, blockchain):
        super().__init__(node)
        self.blockchain = blockchain

    def handle(self, sender, message):
        """
        Handle incoming message
        :param sender: address of sending node (can be used to get connection object)
        :param message: message object sent to you
        :return: None
        """
        # TODO: get transaction, verify it, save it and broadcast forward
        pass
