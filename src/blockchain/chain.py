from typing import Dict, List
import time
from base64 import b64decode
from itertools import islice
from collections import defaultdict

from .block import Block
from .transaction import Transaction
from .chain_wallet import ChainWallet
from .config import Config
from .consensus import wallet_penalty, SumTree
from .next_block_chooser import NextBlockChooser
from .hardcoded import GENESIS_BLOCK, developer_address


from .exceptions import (
    ValidationError,
    InsufficientBalanceError,
    TooMachTransactionInBlockError,
    InvalidSignatureError,
    LowTransactionCounterError,
    InvalidGenesisHashError,
    NonSequentialBlockError,
    BlockChainError,
    InvalidSenderOrRecipient,
)


class Chain:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(_i_know_what_i_doing=True)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def __init__(self, _i_know_what_i_doing: bool = False):
        if not _i_know_what_i_doing:
            raise RuntimeError(
                f"{self.__class__.__name__} is singleton use get_instance class method."
            )
        self.blocks: List[Block] = []
        self.transaction_pool: Dict[
            str, Transaction
        ] = {}  # {transaction_hash: transaction object}
        self.chain_wallets: Dict[
            str, ChainWallet
        ] = {}  # {chain wallet address: chain wallet object}

        self.penalty: int = 0
        self.sum_tree = None
        self.epoch_random = Config.epoch_initial_random

        self.get_chain_wallet(developer_address)
        self._insert_block_to_chain(GENESIS_BLOCK)

        self.next_block_chooser = NextBlockChooser(self)
        self.next_block_chooser.start()

    def get_chain_wallet(self, address: str):
        if address not in self.chain_wallets:
            self.chain_wallets[address] = ChainWallet(
                address,
                balance=Config.test_net_wallet_initial_coins if Config.test_net else 0,
            )
        return self.chain_wallets[address]

    def add_block(self, block_dict: dict):
        block = Block.from_dict(block_dict)
        self.next_block_chooser.scan_block(block)

    def link_new_block(self, block: Block, _i_know_what_i_doing: bool = False):
        if not _i_know_what_i_doing:
            raise RuntimeError(
                "You can't access this sensitive method without _i_know_what_i_doing argument, "
                "You are probable not need to access it directly and should call add_block instead."
            )
        self._process_block(block)

    def add_transaction(self, transaction_dict: dict):
        transaction = Transaction.from_dict(transaction_dict)
        if not self.validate_transaction(transaction):
            raise
        self.transaction_pool[transaction.hash] = transaction

    def create_unsigned_block(self, forger: str):
        index = self._last_block_index + 1
        previous_hash = self._last_block_hash
        timestamp = time.time()
        transactions = list(self._get_transactions(10))
        block = Block(
            index=index,
            previous_hash=previous_hash,
            timestamp=timestamp,
            forger=forger,
            transactions=transactions,
        )
        return block

    def create_unsigned_transaction(
        self, sender: str, recipient: str, amount: float, fee: float, tx_counter: int
    ):
        transaction = Transaction(
            sender=sender,
            recipient=recipient,
            amount=amount,
            fee=fee,
            tx_counter=tx_counter,
        )
        return transaction

    def validate_transaction(self, transaction: Transaction) -> bool:
        sender_wallet = self.get_chain_wallet(transaction.sender)
        if transaction.tx_counter <= sender_wallet.tx_counter:
            raise LowTransactionCounterError(
                "Transaction tx_counter is lower then the wallet tx_counter",
                wallet_counter=sender_wallet.tx_counter,
                transaction_tx_counter=transaction.tx_counter,
            )
        if transaction.amount < 0 or transaction.fee < Config.min_fee:
            raise ValidationError("Invalid transaction arguments")
        if not transaction.signature_verified():
            raise InvalidSignatureError("Invalid transaction signature")
        if transaction.amount + transaction.fee > sender_wallet.balance:
            raise InsufficientBalanceError(
                "Sender wallet balance is too low",
                current=sender_wallet.balance,
                required=transaction.amount + transaction.fee,
            )
        if transaction.sender == transaction.recipient:
            raise InvalidSenderOrRecipient("Sender is recipient")
        return True

    def validate_block(self, block: Block) -> bool:
        if block.index == 0:
            if block.hash != GENESIS_BLOCK.hash:
                raise InvalidGenesisHashError(
                    "Genesis block hash is not hard coded hash"
                )
            return True
        if block.index != self._last_block_index + 1:
            raise NonSequentialBlockError(
                "Block index is not sequential",
                current_index=block.index,
                required_index=self._last_block_index + 1,
            )
        if block.previous_hash != self._last_block_hash:
            raise NonSequentialBlockError(
                "Block previous hash isn't matching previous block hash"
            )
        if not block.signature_verified():
            raise InvalidSignatureError("Invalid block signature")
        if len(block.transactions) > Config.max_transactions_per_block:
            raise TooMachTransactionInBlockError(
                "too mach transactions in block",
                tx_count=len(block.transactions),
                max_transactions=Config.max_transactions_per_block,
            )

        block_wallets = defaultdict(float)  # {str, float}
        for transaction in block.transactions:
            self.validate_transaction(transaction)
            block_wallets[transaction.sender] += transaction.amount + transaction.fee
            if (
                block_wallets[transaction.sender]
                > self.chain_wallets[transaction.sender].balance
            ):
                raise InsufficientBalanceError(
                    "All sender transaction in the block are bigger from his balance",
                    sum_spent=block_wallets[transaction.sender],
                    current_balance=self.chain_wallets[transaction.sender].balance,
                )
        return True

    def block_penalty(self, block: Block) -> int:
        return wallet_penalty(
            self.sum_tree,
            block.forger,
            self.epoch_random,
            list(sorted(self.chain_wallets.keys())),
        )

    def _process_block(self, block: Block):
        self.validate_block(block)
        forger_wallet = self.get_chain_wallet(block.forger)
        fees = 0.0
        for transaction in block.transactions:
            sender_wallet = self.get_chain_wallet(transaction.sender)
            recipient_wallet = self.get_chain_wallet(transaction.recipient)
            sender_wallet.balance -= transaction.amount
            recipient_wallet.balance += transaction.amount
            sender_wallet.balance -= transaction.fee
            fees += transaction.fee
            sender_wallet.update_tx_counter(transaction.tx_counter)
        forger_wallet.balance += fees
        self._insert_block_to_chain(block)

    def _insert_block_to_chain(self, block: Block):
        self.blocks.append(block)
        self.epoch_random = self._next_epoch_random(block.forger)
        for transaction in block.transactions:
            del self.transaction_pool[transaction.hash]
        if self.sum_tree is None or block.index % Config.epoch_size == 0:
            self._build_sum_tree()

    def _next_epoch_random(self, new_block_forger_address: str):
        bytes_compressed_address = b64decode(new_block_forger_address)[1:]
        new_random = int.from_bytes(bytes_compressed_address, "big")
        return new_random / Config.curve.order

    def _build_sum_tree(self):
        self.sum_tree = SumTree.from_dict(
            {address: wallet.balance for address, wallet in self.chain_wallets.items()}
        )

    @property
    def _last_block(self) -> Block:
        return self.blocks[-1]

    @property
    def _last_block_index(self) -> int:
        return self._last_block.index

    @property
    def _last_block_hash(self) -> str:
        return self._last_block.hash

    def _get_transactions(self, count: int):
        count = min(count, len(self.transaction_pool))
        return sorted(
            islice(
                sorted(
                    self.transaction_pool.values(),
                    key=lambda transaction: transaction.fee,
                    reverse=True,
                ),
                max,
            ),
            key=lambda transaction: transaction.tx_counter,
        )
