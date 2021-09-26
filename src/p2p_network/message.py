import json
import base64

from .exceptions import InvalidMessageFormat


__all__ = ["PREFIX", "Message"]


PREFIX = b"636"


class Message:
    def __init__(self, dict_message: dict):
        self.dict_message = dict_message

    @classmethod
    def from_bytes(cls, data: bytes):
        if not data.startswith(PREFIX):
            raise InvalidMessageFormat(f"invalid prefix expected b'{PREFIX.decode()}'")
        data = data[len(PREFIX):]
        json_message = base64.b64decode(data)
        dict_message = json.loads(json_message)
        return cls(dict_message)

    def to_bytes(self) -> bytes:
        return PREFIX + base64.b64encode(json.dumps(self.dict_message).encode())
