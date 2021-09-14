from time import time

from .block import Block

__all__ = ["GENESIS_BLOCK", "developer_address"]

developer_address = "A2tddJpzOWIp1Dv81mqn4WJ/UQAjmFLPINRnkt67zMMR"

GENESIS_BLOCK = Block(
    index=0, previous_hash="0", forger=developer_address, timestamp=time()
)
