__all__ = [
    "BlockChainError",
    "ValidationError",
    "NonSequentialBlockError",
    "LowTransactionCounterError",
    "InvalidGenesisHashError",
    "InvalidSignatureError",
    "TooMachTransactionInBlockError",
    "InsufficientBalanceError",
    "InvalidSenderOrRecipient",
]


class BlockChainError(Exception):
    pass


class ValidationError(BlockChainError):
    def __init__(self, msg: str = None, **kwargs):
        self.msg = msg
        self.kwargs = kwargs

    def __str__(self):
        return f"Message: {self.msg}, Arguments: {self.kwargs}"


class NonSequentialBlockError(ValidationError):
    pass


class LowTransactionCounterError(ValidationError):
    pass


class InvalidGenesisHashError(ValidationError):
    pass


class InvalidSignatureError(ValidationError):
    pass


class TooMachTransactionInBlockError(ValidationError):
    pass


class InsufficientBalanceError(ValidationError):
    pass


class InvalidSenderOrRecipient(ValidationError):
    pass
