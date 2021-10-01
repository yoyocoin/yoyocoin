"""
Block is a class that represent blockchain block
its contain:
- block index
- previous block hash
- block creation timestamp
- block forger wallet public address
- block transactions
- block signature (signed by forger wallet)
"""


from hashlib import sha256

from .transaction import Transaction
from .signed import Signed
from .verifier import Verifier


class Block(Signed):
    def __init__(
        self,
        index: int,
        previous_hash: str,
        timestamp: float,
        forger: str,
        transactions: list = None,
        signature: str = None,
    ):
        if transactions is None:
            transactions = []
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.forger = forger
        self.transactions = transactions

        self.signature = signature

    @property
    def hash(self) -> str:
        """
        :return: Block hash value based on block core data
        """
        return sha256(self._raw_block().encode()).hexdigest()

    @property
    def is_signed(self) -> bool:
        """
        :return: True if block object contains signature
        """
        return self.signature is not None

    @property
    def verifying_key(self) -> str:
        """
        :return: verifying key string for signature verification
        """
        return self.forger

    def _raw_block(self) -> str:
        """
        returns string representation of the core data on the block
        the string is used for signature creation
        :return: string
        """
        return f"{self.index}:{self.previous_hash}:{self.timestamp}:{self.forger}:{[t.to_dict() for t in self.transactions]}"

    def add_signature(self, signature: str):
        """
        Add signature to block
        :param signature: signature data
        :return: None
        """
        self.signature = signature

    def signature_verified(self) -> bool:
        """
        :return: True for verified signature and False for unverified signature
        """
        return self.is_signed and Verifier.is_verified(
            self.verifying_key, self.signature, self.hash  # type: ignore
        )

    def to_dict(self) -> dict:
        """
        return's dict representation of block
        :return: dict
        """
        return {
            "index": self.index,
            "forger": self.forger,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": [
                transaction.to_dict() for transaction in self.transactions
            ],
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, block_dict: dict):
        """
        Create block object from dict representation
        :param block_dict: dict object
        :return: block object
        """
        transactions = [
            Transaction.from_dict(t) for t in block_dict.get("transactions", [])
        ]
        block_dict["transactions"] = transactions
        return cls(**block_dict)
