from typing import Dict, List
import json

from .messages import NewBlock, NewTransaction, PeerInfo
from .messages.message import Message

types: Dict[str, Message] = {clss.typ: clss for clss in [NewBlock, NewTransaction, PeerInfo]}  # type: ignore


class Processor:
    def __init__(self, blockchain, node) -> None:
        self.chain = blockchain
        self.node = node
        self._to_relay: List[bytes] = []

    def process(self, msg: bytes):
        msg_str: str = msg.decode()
        msg_dict: dict = json.loads(msg_str)

        msg_typ = msg_dict["msg"]["typ"]
        msg_cls = types.get(msg_typ, None)
        if msg_cls is None:
            print("unsupported message", msg_typ)
            return
        msg_obj: Message = msg_cls.from_dict(msg_dict)
        print("preccessed msg", msg_obj)
        msg_obj.process(self.chain, self.node)
        self._relay(msg_obj)

    def _relay(self, o_msg: Message):
        o_msg.ttl -= 1
        if o_msg.ttl <= 0:
            return
        self._to_relay.append(o_msg.to_bytes())

    @property
    def relay_messages(self) -> list:
        res = self._to_relay.copy()
        self._to_relay.clear()
        return res
