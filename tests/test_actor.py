import unittest
from time import sleep

from blockchain import Actor, Chain, Config
from blockchain.exceptions import ValidationError


class MyActorTesterOnTestNet(unittest.TestCase):
    def setUp(self) -> None:
        Chain.reset()
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 100
        Config.new_block_interval = 1

    def test_create_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        tx = actor1.create_transaction(recipient=actor2.address, amount=10)
        chain.add_transaction(tx.to_dict())

    def test_forge_empty_block(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor1.forge_block()

    def test_forge_block_with_transaction(self):
        forger = Actor(secret_key="forger_secret!")

        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        tx = actor1.create_transaction(recipient=actor2.address, amount=10)
        chain.add_transaction(tx.to_dict())

        block = forger.forge_block()
        chain.add_block(block.to_dict())

    def test_transaction_to_self(self):
        actor1 = Actor(secret_key="super_secret1!")
        chain = Chain.get_instance()

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor1.address, amount=10)
            chain.add_transaction(tx.to_dict())

    def test_negative_amount_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=-10)
            chain.add_transaction(tx.to_dict())

    def test_negative_fee_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=10, fee=-1)
            chain.add_transaction(tx.to_dict())

    def test_zero_fee_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        with self.assertRaises(ValidationError):
            tx = actor1.create_transaction(recipient=actor2.address, amount=10, fee=0)
            chain.add_transaction(tx.to_dict())

    def test_chain_tx_counter(self):
        forger = Actor(secret_key="forger_secret!")
        sender = Actor(secret_key="super_secret1!")
        recipient = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        tx = sender.create_transaction(recipient=recipient.address, amount=10)
        chain.add_transaction(tx.to_dict())

        tx_counter_before = sender.chain_tx_counter
        block = forger.forge_block()
        chain.add_block(block.to_dict())
        sleep(2)  # wait for block creation
        tx_counter_after = sender.chain_tx_counter

        self.assertGreater(tx_counter_after, tx_counter_before)

    def test_actor_balance(self):
        forger = Actor(secret_key="forger_secret!")

        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        chain = Chain.get_instance()

        transaction_amount = 10
        transaction_fee = 1

        before_transaction_actor2_balance = actor2.balance
        before_transaction_actor1_balance = actor1.balance
        before_transaction_forger_balance = forger.balance

        tx = actor1.create_transaction(
            recipient=actor2.address, amount=transaction_amount, fee=transaction_fee
        )
        chain.add_transaction(tx.to_dict())
        block = forger.forge_block()
        chain.add_block(block.to_dict())
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
