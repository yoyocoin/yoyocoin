"""
Protocol that handle block broadcast
1. deserialize data
2. load block from ipfs
3. add to lottery system
4. broadcast forward block cid
"""

from p2p_network.protocol import Protocol
from p2p_network.message import Message
from blockchain import Chain
from blockchain.exceptions import ValidationError

from ..ipfs import Ipfs


class BlockProtocol(Protocol):
    name = "blocks"

    def __init__(self, node):
        super().__init__(node)
        self.ipfs = Ipfs.get_instance()

    @property
    def blockchain(self):
        return Chain.get_instance()

    def handle(self, sender, message):
        """
        Handle incoming message
        :param sender: address of sending node (can be used to get connection object)
        :param message: message object sent to you
        :return: None
        """
        if message.dict_message.get("action", None) == "new-block":
            block_cid = message.dict_message["block"]
            block_dict = self.ipfs.load_cid(block_cid)
            try:
                self.blockchain.add_block(block_dict)
            except ValidationError:
                # TODO: if larger index sync else ignore
                raise
            self._broadcast_forward(message, sender)

    def _broadcast_forward(self, message, sender):
        # TODO: only forward currently winning block for network optimization
        self.node.broadcast(message, exclude=[sender])

    @classmethod
    def create_broadcast_block_message(cls, block_dict: dict) -> Message:
        ipfs = Ipfs.get_instance()
        block_cid = ipfs.create_cid(block_dict)
        return Message(
            dict_message={"protocol": cls.name, "action": "new-block", "block": block_cid},
            broadcast=True,
        )
