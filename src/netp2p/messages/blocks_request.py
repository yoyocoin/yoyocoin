from .message import Message
from .blocks_response import BlocksResponse


class BlocksRequest(Message):
    typ = "blocks-request"

    def __init__(self, start_index, end_index, **kwargs) -> None:
        self.start_index = start_index
        self.end_index = end_index
        super().__init__(self.__class__.typ, ttl=1)

    def to_dict(self) -> dict:
        return {
            "msg": super().to_dict(),
            "start_index": self.start_index,
            "end_index": self.end_index,
        }

    def process(self, blockchain, node):
        print("Sending blocks")
        if blockchain.is_full():
            response = BlocksResponse(
                blocks=[
                    b.to_dict()
                    for b in blockchain.blocks[self.start_index: self.end_index]
                ]
            ).to_bytes()
        else:
            response = b""
        return response

    @classmethod
    def from_dict(cls, dict_: dict):
        msg_typ = dict_["msg"]["typ"]
        if msg_typ != cls.typ:
            raise TypeError(f"invalid message type '{msg_typ}' required '{cls.typ}'")
        return cls(dict_["start_index"], dict_["end_index"], **dict_["msg"])

    def __str__(self) -> str:
        return f"{self.__class__.__name__}('ttl'={self.ttl}, 'start_index': {self.start_index}, 'end_index': {self.end_index})"
