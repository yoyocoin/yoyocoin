import unittest

from blockchain import Actor, Chain, Config


class MyActorTesterOnTestNet(unittest.TestCase):
    def setUp(self) -> None:
        Chain.reset()
        Config.test_net = True
        Config.test_net_wallet_initial_coins = 100

    def test_create_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        actor1.transfer_coins(recipient=actor2.address, amount=10)

    def test_forge_empty_block(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor1.forge_block()

    def test_forge_block_with_transaction(self):
        forger = Actor(secret_key="forger_secret!")

        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        actor1.transfer_coins(recipient=actor2.address, amount=10)

        forger.forge_block()

    def test_transaction_to_self(self):
        actor1 = Actor(secret_key="super_secret1!")
        with self.assertRaises(Exception):
            actor1.transfer_coins(recipient=actor1.address, amount=10)

    def test_negative_amount_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        with self.assertRaises(Exception):
            actor1.transfer_coins(recipient=actor2.address, amount=-10)

    def test_negative_fee_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        with self.assertRaises(Exception):
            actor1.transfer_coins(recipient=actor2.address, amount=10, fee=-1)

    def test_zero_fee_transaction(self):
        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")
        with self.assertRaises(Exception):
            actor1.transfer_coins(recipient=actor2.address, amount=10, fee=0)

    def test_actor_balance(self):
        forger = Actor(secret_key="forger_secret!")

        actor1 = Actor(secret_key="super_secret1!")
        actor2 = Actor(secret_key="super_secret2!")

        transaction_amount = 10
        transaction_fee = 1

        before_transaction_actor2_balance = actor2.balance
        before_transaction_actor1_balance = actor1.balance
        before_transaction_forger_balance = forger.balance

        actor1.transfer_coins(recipient=actor2.address, amount=transaction_amount, fee=transaction_fee)
        forger.forge_block()

        after_transaction_actor2_balance = actor2.balance
        after_transaction_actor1_balance = actor1.balance
        after_transaction_forger_balance = forger.balance

        self.assertEqual(
            before_transaction_actor1_balance - transaction_amount - transaction_fee, after_transaction_actor1_balance
        )
        self.assertEqual(before_transaction_actor2_balance + transaction_amount, after_transaction_actor2_balance)
        self.assertEqual(before_transaction_forger_balance + transaction_fee, after_transaction_forger_balance)

if __name__ == '__main__':
    unittest.main()
