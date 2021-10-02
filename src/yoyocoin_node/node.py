from p2p_network import Node, Connection
from blockchain import Chain

from .coin_protocols import TransactionProtocol, BlockProtocol


class YoyocoinNode(Node):
    def __init__(self, host: str):
        self.__class__.LISTEN_HOST = host  # for Local testing
        self.blockchain: Chain = Chain.get_instance()
        self.protocols = [TransactionProtocol(self, self.blockchain), BlockProtocol(self, self.blockchain)]
        super().__init__(protocols=self.protocols)

    def on_message(self, message):
        sender, data = message
        print(sender, data)

    def on_new_connection(self, connection: Connection):
        pass

    def on_connection_closed(self, connection: Connection):
        pass

    def broadcast_transaction(self, transaction_dict: dict):
        self.broadcast(TransactionProtocol.create_broadcast_transaction_message(transaction_dict))

    def broadcast_candidate_block(self, block_dict: dict):
        self.broadcast(BlockProtocol.create_broadcast_block_message(block_dict))
