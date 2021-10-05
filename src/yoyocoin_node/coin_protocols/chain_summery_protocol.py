"""
Protocol that handle chain summery
"""

from p2p_network.protocol import Protocol
from p2p_network.message import Message
from blockchain import Chain
from ..ipfs import Ipfs


class ChainSummeryProtocol(Protocol):
    name = "chain-summery"

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
        if message.dict_message.get("action", None) == "summery-request":
            connection = self.node.get_connection(sender)
            cids = []
            my_summery = self.blockchain.summery
            for block in self.blockchain.blocks:
                cids.append(self.ipfs.create_cid(block.to_dict()))
            connection.send(self.create_chain_summery_response_message(my_summery.to_dict(), cids).to_bytes())

    @classmethod
    def create_chain_summery_request_message(cls) -> Message:
        return Message(dict_message={"protocol": cls.name, "action": "summery-request"})

    @classmethod
    def create_chain_summery_response_message(cls, summery: dict, cids: list) -> Message:
        return Message(dict_message={"summery": summery, "cids": cids})
