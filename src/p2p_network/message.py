import json
import base64
from hashlib import sha256

__all__ = ["Message"]


MAX_TTL = 10
META_KEY = 'meta'


class Message:
    def __init__(self, dict_message: dict, broadcast: bool = False, ttl: int = None):
        """ Create Message object
        :param dict_message: dict values to send
        :param broadcast: is this message is broadcast message
        :param ttl: limit amount of hops for broadcast message
        """
        if ttl is None:
            ttl = MAX_TTL
        self.dict_message = dict_message
        self.is_broadcast = broadcast
        self.ttl = ttl
        self.hash = self._get_hash()

    def _get_hash(self) -> str:
        return sha256(json.dumps(self.dict_message).encode()).hexdigest()

    @property
    def _full_dict(self):
        """
        The dict object acutely sent over the network
        :return: dict data + meta data
        """
        meta = {"broadcast": self.is_broadcast, "ttl": self.ttl}
        return {**self.dict_message, META_KEY: meta}

    @classmethod
    def from_bytes(cls, data: bytes):
        json_message = base64.b64decode(data)
        dict_message = json.loads(json_message)
        meta = dict_message.pop(META_KEY)
        meta['ttl'] -= 1
        return cls(dict_message, **meta)

    def is_valid(self) -> bool:
        return MAX_TTL >= self.ttl > 0

    def to_bytes(self) -> bytes:
        return base64.b64encode(json.dumps(self._full_dict).encode())
