from base64 import b64encode

from ecdsa.keys import SigningKey  # type: ignore

from .config import Config


class Wallet:
    def __init__(self, secret_password: str = None):
        self.secret = secret_password
        if self.secret is not None:
            secret_hash_bytes = Config.hashfunc(self.secret.encode()).digest()
            secret_int = int.from_bytes(secret_hash_bytes, "big") % Config.curve.order
            self.signing_key = SigningKey.from_secret_exponent(
                secexp=secret_int, curve=Config.curve, hashfunc=Config.hashfunc
            )
        else:
            self.signing_key = SigningKey.generate(
                curve=Config.curve, hashfunc=Config.hashfunc
            )

        self.verifying_key = self.signing_key.get_verifying_key()

    @property
    def address(self) -> str:
        return b64encode(self.verifying_key.to_string(encoding="compressed")).decode()

    def sign(self, hash_str: str) -> str:
        return b64encode(
            self.signing_key.sign(hash_str.encode(), hashfunc=Config.hashfunc)
        ).decode()
