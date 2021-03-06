"""
Actor is a class that expose simple api for working with the blockchain has a wallet owner

get wallet address

get wallet balance

get wallet transactions counter

transfer coins to other wallet

forge new block
"""


from .block import Block
from .chain import Chain
from .transaction import Transaction
from .wallet import Wallet
from .config import Config


class Actor:
    def __init__(self, secret_key: str, blockchain: Chain):
        self.wallet = Wallet(secret_password=secret_key)
        self.blockchain = blockchain

        self.wallet_balance = 100

        self.tx_counter = 1

    @property
    def _chain_wallet(self):
        return self.blockchain.get_chain_wallet(self.address)

    @property
    def address(self) -> str:
        return self.wallet.address

    @property
    def balance(self) -> float:
        """
        :return: Wallet coins balance
        """
        return self._chain_wallet.balance

    @property
    def chain_tx_counter(self) -> int:
        """
        :return: Number of transactions the wallet created (used for transaction nonce)
        """
        return self._chain_wallet.tx_counter

    def create_transaction(
        self, recipient: str, amount: int, fee: int = Config.min_fee
    ) -> Transaction:
        """Transfer coins to other wallet
        :param recipient: wallet address to transfer the coins
        :param amount: amount of coins to transfer
        :param fee: transaction fee to speed up transaction processing (minimum value required)
        :return: None
        """
        transaction = Chain.create_unsigned_transaction(
            sender=self.wallet.address,
            recipient=recipient,
            amount=amount,
            fee=fee,
            tx_counter=self.tx_counter,
        )
        signature = self.wallet.sign(transaction.hash)
        transaction.add_signature(signature)
        self.tx_counter += 1
        return transaction

    def forge_block(self) -> Block:
        """
        Creating new block of transactions
        :return: block
        """
        block = self.blockchain.create_unsigned_block(self.wallet.address)
        signature = self.wallet.sign(block.hash)
        block.add_signature(signature)
        return block
