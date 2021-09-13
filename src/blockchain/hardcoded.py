from time import time

from .block import Block
from .wallet import Wallet

__all__ = ["GENESIS_BLOCK", "developer_address"]

developer_wallet = Wallet(secret_password="some_password")
developer_address = developer_wallet.address
# TODO: save only public key on production

GENESIS_BLOCK = Block(index=0, previous_hash="0", forger=developer_wallet.address, timestamp=time())
