import unittest
from time import sleep

from blockchain import Actor, Chain, Config
from blockchain.exceptions import ValidationError


class MyActorTesterOnTestNet(unittest.TestCase):
    def setUp(self) -> None:
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 100
        Config.new_block_interval = 1

    def test_create_transaction(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        tx = actor1.create_transaction(recipient=actor2.address, amount=10)
        blockchain.add_transaction(tx.to_dict())

    def test_forge_empty_block(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        block = actor1.forge_block()
        blockchain.add_block(block.to_dict())

    def test_forge_block_with_transaction(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_secret!", blockchain=blockchain)

        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        tx = actor1.create_transaction(recipient=actor2.address, amount=10)
        blockchain.add_transaction(tx.to_dict())

        block = forger.forge_block()
        blockchain.add_block(block.to_dict())

    def test_transaction_to_self(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor1.address, amount=10)
            blockchain.add_transaction(tx.to_dict())

    def test_negative_amount_transaction(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=-10)
            blockchain.add_transaction(tx.to_dict())

    def test_negative_fee_transaction(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=10, fee=-1)
            blockchain.add_transaction(tx.to_dict())

    def test_zero_fee_transaction(self):
        blockchain = Chain()
        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=10, fee=0)
            blockchain.add_transaction(tx.to_dict())

    def test_chain_tx_counter(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_secret!", blockchain=blockchain)
        sender = Actor(secret_key="super_secret1!", blockchain=blockchain)
        recipient = Actor(secret_key="super_secret2!", blockchain=blockchain)

        tx = sender.create_transaction(recipient=recipient.address, amount=10)
        blockchain.add_transaction(tx.to_dict())

        tx_counter_before = sender.chain_tx_counter
        block = forger.forge_block()
        blockchain.add_block(block.to_dict())
        sleep(2)  # wait for block creation
        tx_counter_after = sender.chain_tx_counter

        self.assertGreater(tx_counter_after, tx_counter_before)

    def test_actor_balance(self):
        blockchain = Chain()
        forger = Actor(secret_key="forger_secret!", blockchain=blockchain)

        actor1 = Actor(secret_key="super_secret1!", blockchain=blockchain)
        actor2 = Actor(secret_key="super_secret2!", blockchain=blockchain)

        transaction_amount = 10
        transaction_fee = 1

        before_transaction_actor2_balance = actor2.balance
        before_transaction_actor1_balance = actor1.balance
        before_transaction_forger_balance = forger.balance

        tx = actor1.create_transaction(
            recipient=actor2.address, amount=transaction_amount, fee=transaction_fee
        )
        blockchain.add_transaction(tx.to_dict())
        block = forger.forge_block()
        blockchain.add_block(block.to_dict())
        sleep(
            2
        )  # Wait until the block is added, we set the block adding interval to 1 in the setUp method

        after_transaction_actor2_balance = actor2.balance
        after_transaction_actor1_balance = actor1.balance
        after_transaction_forger_balance = forger.balance

        self.assertEqual(
            before_transaction_actor1_balance - transaction_amount - transaction_fee,
            after_transaction_actor1_balance,
        )
        self.assertEqual(
            before_transaction_actor2_balance + transaction_amount,
            after_transaction_actor2_balance,
        )
        self.assertEqual(
            before_transaction_forger_balance + transaction_fee,
            after_transaction_forger_balance,
        )
