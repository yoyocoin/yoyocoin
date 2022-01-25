import json


class Processor:
    def __init__(self, blockchain, node) -> None:
        self.chain = blockchain
        self.node = node
        self._to_relay = []

    def deaserialize(self, msg: bytes) -> str:
        return msg.decode()
    
    def serialize(self, msg: str) -> bytes:
        return msg.encode()

    def dict_to_json(self, d: dict) -> str:
        return json.dumps(d) 

    def json_to_dict(self, msg: str) -> dict:
        return json.loads(msg)

    def process(self, msg: bytes):
        msg = self.deaserialize(msg)
        m_dict = self.json_to_dict(msg)

        print("preccessed msg", m_dict)
        if m_dict["msg"] == "new-block":
            pass
        elif m_dict["msg"] == "new-transaction":
            pass
        elif m_dict["msg"] == "peer-info":
            node_addr = m_dict["addr"]
            print("adding peer info", node_addr)
            self.node.nodes.add(tuple(node_addr))
        self._relay(m_dict)
    
    def _relay(self, m_dict: dict):
        m_dict["ttl"] -= 1
        if m_dict["ttl"] <= 0:
            return
        msg = self.dict_to_json(m_dict)
        msg = self.serialize(msg)
        self._to_relay.append(msg)

    @property
    def relay_messages(self) -> list:
        res = self._to_relay.copy()
        self._to_relay.clear()
        return res