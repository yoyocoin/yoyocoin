import json
import base64


class Message:
    def __init__(self, dict_message: dict):
        self.dict_message = dict_message

    @classmethod
    def from_bytes(cls, data: bytes):
        json_message = base64.b64decode(data)
        dict_message = json.loads(json_message)
        return cls(dict_message)

    def to_bytes(self):
        return base64.b64encode(json.dumps(self.dict_message).encode())
