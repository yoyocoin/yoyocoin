import unittest

from blockchain.consensus import wallet_penalty, SumTree


class LotteryTester(unittest.TestCase):
    def test_sum_tree_lottery(self):
        wallets = {"a": 1, "b": 100, "c": 1}
        sorted_wallets = sorted(wallets.keys())

        sum_tree = SumTree.from_dict(wallets)
        winning_distance = wallet_penalty(sum_tree, "b", lottery_number=0.5, wallets_sorted_by_address=sorted_wallets)
        self.assertEqual(winning_distance, 0)

        right_distance = wallet_penalty(sum_tree, "c", lottery_number=0.5, wallets_sorted_by_address=sorted_wallets)
        self.assertEqual(right_distance, 1.1)  # right is getting 0.1 more then left for tie break

        left_distance = wallet_penalty(sum_tree, "a", lottery_number=0.5, wallets_sorted_by_address=sorted_wallets)
        self.assertEqual(left_distance, 1)

        a_winning = wallet_penalty(sum_tree, "a", lottery_number=0.001, wallets_sorted_by_address=sorted_wallets)
        self.assertEqual(a_winning, 0)
