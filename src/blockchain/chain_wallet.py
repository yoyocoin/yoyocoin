"""
ChainWallet is object representation of wallet data
the object contains:
wallet address
wallet balance
wallet tx counter (how many transactions the wallet has made)

the object expose methods for updating the wallet data:
add_coins (add coins amount to balance)
subtract_coins (subtract coins amount from balance)
update_tx_counter (update number of transactions made with the wallet)
"""


class ChainWallet:
    def __init__(self, address: str, balance: float = 0.0, tx_counter: int = 0):
        self.address = address
        self.balance = balance
        self.tx_counter = tx_counter

    def add_coins(self, amount: float):
        self.balance += amount

    def subtract_coins(self, amount: float):
        self.balance -= amount

    def update_tx_counter(self, update_tx_counter: int):
        self.tx_counter = update_tx_counter
