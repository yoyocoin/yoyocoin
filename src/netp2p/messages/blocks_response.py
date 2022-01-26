from blockchain import Chain, exceptions
from blockchain.block import Block

from .message import Message


class BlocksResponse(Message):
    typ = "blocks-response"

    def __init__(self, blocks, **kwargs) -> None:
        """
        :blocks: list of dict (blocks in a dict representaion)
        """
        self.blocks = blocks
        super().__init__(self.__class__.typ, ttl=1)

    def to_dict(self) -> dict:
        return {"msg": super().to_dict(), "blocks": self.blocks}

    def process(self, blockchain, node):
        print("Recving blocks and updating blockchain")
        update_branch: Chain = blockchain.copy()
        try:
            for new_b_d in self.blocks:
                b = Block.from_dict(new_b_d)
                update_branch.link_new_block(b, _i_know_what_i_doing=True)
        except exceptions.BlockChainError:
            return # The new update is invalid
        blockchain.update_state(update_branch)

    @classmethod
    def from_dict(cls, dict_: dict):
        msg_typ = dict_["msg"]["typ"]
        if msg_typ != cls.typ:
            raise TypeError(f"invalid message type '{msg_typ}' required '{cls.typ}'")
        return cls(dict_["blocks"], **dict_["msg"])

    def __str__(self) -> str:
        return f"{__class__.__name__}('ttl'={self.ttl}, 'blocks': {self.blocks})"
