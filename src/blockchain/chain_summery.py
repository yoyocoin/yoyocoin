from typing import List


class ChainSummery:
    def __init__(self, blocks: List[str], penalty: int):
        self.blocks = blocks
        self.length = len(self.blocks)
        self.penalty = penalty

    @classmethod
    def from_dict(cls, dict_data: dict):
        return cls(dict_data["blocks"], dict_data["score"])

    def to_dict(self):
        return {
            "blocks": self.blocks,
            "score": self.penalty,
        }

    def diff(self, other):
        """
        Return list of blocks to replace for syncing
        :param other: ChainSummery object
        :return: block index to start update from, list of blocks
        """
        diff_start: int = 0
        for index, my_block_hash, other_block_hash in enumerate(zip(self.blocks, other.blocks)):
            if my_block_hash == other_block_hash:
                diff_start += index
            else:
                break
        return diff_start, other.blocks[diff_start:]

    def __eq__(self, other):
        return self.penalty == other.score and self.length == self.length

    def __gt__(self, other):
        return self.penalty < other.score and self.length >= self.length
