from .message import Message

class PeerInfo(Message):
    typ = "peer-info"

    def __init__(self, addr, ttl=10, **kwargs) -> None:
        self.addr = addr

        super().__init__(self.__class__.typ, ttl=ttl)
    
    def dict(self) -> dict:
        return {"msg": super().dict(), "addr": self.addr}
    
    def process(self, blockchain, node):
        print("adding peer info", self.addr)
        node.nodes.add(tuple(self.addr))

    @classmethod
    def from_dict(cls, dict_: dict):
        msg_typ = dict_["msg"]["typ"]
        if msg_typ != cls.typ:
            raise TypeError(f"invalid message type '{msg_typ}' required '{cls.typ}'")
        return cls(dict_["addr"], **dict_["msg"])

    def __str__(self) -> str:
        return f"PeerInfo('ttl'={self.ttl}, 'addr': {self.addr})"
