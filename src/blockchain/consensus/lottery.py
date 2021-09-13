from bisect import bisect_left
from functools import lru_cache

from .sum_tree import SumTree


def _binary_search(array, element):
    i = bisect_left(array, element)
    if i != len(array) and array[i] == element:
        return i
    else:
        return -1


@lru_cache(maxsize=1)
def _find_lottery_winner(root: SumTree, lottery_number: float) -> int:
    """
    Find lottery winner index

    :param root: the root node of the sum tree
    :param lottery_number: float number in range of 0 to 1
    :return: winner wallet index
    """
    search_number = lottery_number * root.sum
    winner = root.search(search_number)
    return winner


def _wallet_distance(winner_index: int, wallet_index: int, wallets_count: int):
    # The 0.1 is added for tie break
    return min(
        abs(winner_index - wallet_index) + 0.1,
        winner_index + (wallets_count - wallet_index),
    )


def wallet_penalty(
    root: SumTree,
    wallet_address: str,
    lottery_number: float,
    wallets_sorted_by_address: list,
):
    wallets_count = len(wallets_sorted_by_address)
    winner_index = _find_lottery_winner(root, lottery_number)
    wallet_index = _binary_search(wallets_sorted_by_address, wallet_address)
    return _wallet_distance(winner_index, wallet_index, wallets_count)
