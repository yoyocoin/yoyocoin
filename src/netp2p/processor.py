import json

from .messages import NewBlock, NewTransaction, PeerInfo
from .messages.message import Message


types = {clss.typ: clss for clss in [NewBlock, NewTransaction, PeerInfo]}


class Processor:
    def __init__(self, blockchain, node) -> None:
        self.chain = blockchain
        self.node = node
        self._to_relay = []

    def _deaserialize(self, msg: bytes) -> str:
        return msg.decode()
    
    def _serialize(self, msg: str) -> bytes:
        return msg.encode()

    def _dict_to_json(self, d: dict) -> str:
        return json.dumps(d)

    def _json_to_dict(self, msg: str) -> dict:
        return json.loads(msg)

    def process(self, msg: bytes):
        msg = self._deaserialize(msg)
        m_dict = self._json_to_dict(msg)
        
        msg_typ = m_dict["msg"]["typ"]
        msg_cls = types.get(msg_typ, None)
        if msg_cls is None:
            print("unsupported message", msg_typ)
            return
        o_msg = msg_cls.from_dict(m_dict)
        print("preccessed msg", o_msg)
        o_msg.process(self.chain, self.node)
        self._relay(o_msg)
    
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
