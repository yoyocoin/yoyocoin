from ecdsa.curves import SECP256k1
from hashlib import sha256


class Config:
    curve = SECP256k1
    hashfunc = sha256

    epoch_initial_random = 0.5
    epoch_size = 100

    min_fee = 1
    max_transactions_per_block = 100

    test_net = False
    test_net_wallet_initial_coins = 100
