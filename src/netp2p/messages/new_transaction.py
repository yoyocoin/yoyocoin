from .message import Message


class NewTransaction(Message):
    typ = "new-transaction"

    def __init__(self, transaction, ttl=10, **kwargs) -> None:
        self.transaction = transaction

        super().__init__(self.__class__.typ, ttl=ttl)

    def to_dict(self) -> dict:
        return {"msg": super().to_dict(), "transaction": self.transaction}

    def process(self, blockchain, node):
        print("Adding transaction")
        blockchain.add_transaction(self.transaction)

    @classmethod
    def from_dict(cls, dict_: dict):
        msg_typ = dict_["msg"]["typ"]
        if msg_typ != cls.typ:
            raise TypeError(f"invalid message type '{msg_typ}' required '{cls.typ}'")
        return cls(dict_["transaction"], **dict_["msg"])

    def __str__(self) -> str:
        return f"NewTransaction('ttl'={self.ttl}, 'transaction': {self.transaction})"
