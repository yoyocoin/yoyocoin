from base64 import b64decode

from ecdsa.keys import VerifyingKey, BadSignatureError  # type: ignore

from .config import Config


class Verifier:
    @staticmethod
    def is_verified(verifying_key_str: str, signature: str, hash_str: str) -> bool:
        verifying_key = VerifyingKey.from_string(
            b64decode(verifying_key_str), curve=Config.curve, hashfunc=Config.hashfunc
        )
        try:
            verifying_key.verify(
                b64decode(signature), hash_str.encode(), hashfunc=Config.hashfunc
            )
        except BadSignatureError:
            return False
        else:
            return True
