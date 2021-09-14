from hashlib import sha256

from .signed import Signed
from .verifier import Verifier


class Transaction(Signed):
    def __init__(
        self,
        sender: str,
        recipient: str,
        amount: float,
        fee: float,
        tx_counter: int,
        signature: str = None,
    ):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.fee = fee
        self.tx_counter = tx_counter

        self.signature = signature

    def add_signature(self, signature):
        self.signature = signature

    @property
    def verifying_key(self) -> str:
        return self.sender

    @property
    def is_signed(self) -> bool:
        return self.signature is not None

    @property
    def hash(self) -> str:
        return sha256(self._raw_transaction().encode()).hexdigest()

    def _raw_transaction(self) -> str:
        return (
            f"{self.sender}:{self.recipient}:{self.amount}:{self.fee}:{self.tx_counter}"
        )

    def signature_verified(self) -> bool:
        return self.is_signed and Verifier.is_verified(
            self.verifying_key, self.signature, self.hash  # type: ignore
        )

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "tx_counter": self.tx_counter,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, transaction_dict: dict):
        return cls(**transaction_dict)
