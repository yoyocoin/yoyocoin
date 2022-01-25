import json


class Message:
    def __init__(self, typ: str, ttl: int = 10) -> None:
        self.typ = typ
        self.ttl = ttl

    def process(self, blockchain, node):
        pass  # TODO require sub class to implement

    def to_dict(self) -> dict:
        return {"typ": self.typ, "ttl": self.ttl}

    def to_bytes(self) -> bytes:
        return json.dumps(self.to_dict()).encode()

    @classmethod
    def from_bytes(cls, bytes_msg: bytes):
        dict_msg = json.loads(bytes_msg.decode())
        return cls.from_dict(dict_msg)

    @classmethod
    def from_dict(cls, d: dict):
        pass
