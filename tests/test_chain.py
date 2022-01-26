import unittest
from time import time

from blockchain import Chain, Actor, Config
from blockchain.block import Block
from blockchain.wallet import Wallet
from blockchain.exceptions import (
    InvalidSignatureError,
    TooMachTransactionInBlockError,
    NonSequentialBlockError,
    InsufficientBalanceError,
    LowTransactionCounterError,
    InvalidGenesisHashError,
)


class MyChainTester(unittest.TestCase):
    def setUp(self) -> None:
        Config.new_block_interval = 1  # seconds

    def test_epoch_random_updater_distribution(self):
        chain = Chain()
        sample_size = 2000
        results = []
        for counter in range(sample_size):
            w = Wallet(secret_password=str(counter))
            results.append(chain._next_epoch_random(w.address))
        self.assertAlmostEqual(sum(results) / len(results), 0.5, delta=0.05)

        distribution_sections = 10
        total = 1
        distribution = [0] * distribution_sections

        for result in results:
            section_size = total / distribution_sections
            distribution[round(result / section_size) - 1] += 1

        precision = 0.3
        self.assertTrue(
            max(distribution) - min(distribution)
            < (sample_size / distribution_sections) * precision
        )

    def test_add_valid_block(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_key", blockchain=blockchain)

        block = forger.forge_block()
        blockchain.link_new_block(block, _i_know_what_i_doing=True)

    def test_pruned_blockchain(self):
        """Test blockchain that save only the last block"""
        blockchain = Chain(save_all_blocks=False)
        forger = Actor(secret_key="forger_key", blockchain=blockchain)

        block = forger.forge_block()
        blockchain.link_new_block(block, _i_know_what_i_doing=True)
        block2 = forger.forge_block()
        blockchain.link_new_block(block2, _i_know_what_i_doing=True)
        self.assertEqual(len(blockchain.blocks), 1)

    def test_add_unsigned_block(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        unsigned_block = blockchain.create_unsigned_block(forger=forger.address)
        with self.assertRaises(InvalidSignatureError):
            blockchain.link_new_block(unsigned_block, _i_know_what_i_doing=True)

    def test_add_bad_signature_block(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        non_forger = Actor(secret_key="non_forger_key", blockchain=blockchain)

        unsigned_block = blockchain.create_unsigned_block(forger=forger.address)
        bad_signature = non_forger.wallet.sign(unsigned_block.hash)
        unsigned_block.add_signature(bad_signature)
        with self.assertRaises(InvalidSignatureError):
            blockchain.link_new_block(unsigned_block, _i_know_what_i_doing=True)

    def test_add_unsigned_transaction(self):
        blockchain = Chain()
        sender = Actor(secret_key="sender_key", blockchain=blockchain)
        recipient = Actor(secret_key="recipient_key", blockchain=blockchain)

        valid_unsigned_transaction = blockchain.create_unsigned_transaction(
            sender=sender.address,
            recipient=recipient.address,
            amount=10,
            fee=1,
            tx_counter=1,
        )
        with self.assertRaises(InvalidSignatureError):
            blockchain.add_transaction(valid_unsigned_transaction.to_dict())

    def test_add_bad_signature_transaction(self):
        blockchain = Chain()
        sender = Actor(secret_key="sender_key", blockchain=blockchain)
        recipient = Actor(secret_key="recipient_key", blockchain=blockchain)

        valid_unsigned_transaction = blockchain.create_unsigned_transaction(
            sender=sender.address,
            recipient=recipient.address,
            amount=10,
            fee=1,
            tx_counter=1,
        )
        signature = recipient.wallet.sign(valid_unsigned_transaction.hash)
        valid_unsigned_transaction.add_signature(
            signature
        )  # add bad signature (recipient signature is invalid)
        with self.assertRaises(InvalidSignatureError):
            blockchain.add_transaction(valid_unsigned_transaction.to_dict())

    def test_bigger_then_allowed_block(self):
        Config.max_transactions_per_block = 1
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 100
        blockchain = Chain()

        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        sender = Actor(secret_key="sender_key", blockchain=blockchain)
        recipient = Actor(secret_key="recipient_key", blockchain=blockchain)

        for _ in range(2):
            tx = sender.create_transaction(recipient.address, 10)
            blockchain.add_transaction(tx.to_dict())

        index = blockchain._last_block_index + 1
        previous_hash = blockchain._last_block_hash
        timestamp = time()
        transactions = list(
            blockchain._get_transactions(Config.max_transactions_per_block + 1)
        )  # more then allowed
        block = Block(
            index=index,
            previous_hash=previous_hash,
            timestamp=timestamp,
            forger=forger.address,
            transactions=transactions,
        )
        signature = forger.wallet.sign(block.hash)
        block.add_signature(signature)

        with self.assertRaises(TooMachTransactionInBlockError):
            blockchain.add_block(block.to_dict())

    def test_add_non_sequential_index_block(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        unsigned_block = blockchain.create_unsigned_block(forger=forger.address)
        unsigned_block.index = 100
        signature = forger.wallet.sign(unsigned_block.hash)
        unsigned_block.add_signature(signature)

        with self.assertRaises(NonSequentialBlockError):
            blockchain.link_new_block(unsigned_block, _i_know_what_i_doing=True)

    def test_add_non_sequential_hash_block(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        unsigned_block = blockchain.create_unsigned_block(forger=forger.address)
        unsigned_block.previous_hash = "bad hash"
        signature = forger.wallet.sign(unsigned_block.hash)
        unsigned_block.add_signature(signature)

        with self.assertRaises(NonSequentialBlockError):
            blockchain.link_new_block(unsigned_block, _i_know_what_i_doing=True)

    def test_add_insufficient_balance_transaction(self):
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 10

        blockchain = Chain()
        sender = Actor(secret_key="sender_key", blockchain=blockchain)
        recipient = Actor(secret_key="recipient_key", blockchain=blockchain)

        with self.assertRaises(InsufficientBalanceError):
            tx = sender.create_transaction(
                recipient.address, Config.test_net_wallet_initial_coins + 1
            )
            blockchain.add_transaction(tx.to_dict())

    def test_add_low_tx_counter(self):
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 100

        blockchain = Chain()
        sender = Actor(secret_key="sender_key", blockchain=blockchain)
        recipient = Actor(secret_key="recipient_key", blockchain=blockchain)

        sender.tx_counter = -1

        with self.assertRaises(LowTransactionCounterError):
            tx = sender.create_transaction(recipient.address, 10)
            blockchain.add_transaction(tx.to_dict())

    def test_invalid_genesis_block(self):
        blockchain = Chain()
        blockchain.blocks.clear()  # remove default genesis

        forger = Actor(secret_key="forger_key", blockchain=blockchain)
        genesis = Block(
            index=0, previous_hash="0", forger=forger.address, timestamp=time()
        )

        with self.assertRaises(InvalidGenesisHashError):
            blockchain.add_block(genesis.to_dict())
