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
