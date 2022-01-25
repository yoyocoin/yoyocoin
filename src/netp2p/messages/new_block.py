from .message import Message


class NewBlock(Message):
    typ = "new-block"

    def __init__(self, block, ttl=10, **kwargs) -> None:
        self.block = block
        super().__init__(self.__class__.typ, ttl=ttl)

    def to_dict(self) -> dict:
        return {"msg": super().to_dict(), "block": self.block}

    def process(self, blockchain, node):
        print("Adding candidate block")
        blockchain.add_block(self.block)

    @classmethod
    def from_dict(cls, dict_: dict):
        msg_typ = dict_["msg"]["typ"]
        if msg_typ != cls.typ:
            raise TypeError(f"invalid message type '{msg_typ}' required '{cls.typ}'")
        return cls(dict_["block"], **dict_["msg"])

    def __str__(self) -> str:
        return f"NewBlock('ttl'={self.ttl}, 'block': {self.block})"
