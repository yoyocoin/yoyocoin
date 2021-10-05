"""
Lottery system, chooses the next block added to the chain
the wining block is randomly selected
block can have bigger probability winning if the block forger have more coins in his wallet
after winning the forger wallet cant win again for some number of blocks

The NextBlockChooser check all the candidate block and choose the block with the least penalty score
block is added every fixed interval of seconds
"""
from threading import Thread
from time import time, sleep
from queue import Queue, Empty

from loguru import logger

from .config import Config
from .block import Block
from .exceptions import ValidationError


class NextBlockChooser(Thread):
    def __init__(self, chain):
        super().__init__(daemon=True)
        self.chain = chain

        self.blocks_queue = Queue()

        self.__current_best_block = None
        self.__best_block_penalty = None
        self.__pause = False
        self.__stop = False

    def scan_block(self, block: Block):
        try:
            self.chain.validate_block(block)
        except ValidationError:
            # Retry on block that sent sooner
            if block.index - self.chain._last_block_index != 1:
                raise
            sleep(2)  # Make sure the previous block has added to the chain
            self.chain.validate_block(block)  # try again
        self.blocks_queue.put(item=block)

    def _check_block(self):
        try:
            block: Block = self.blocks_queue.get(timeout=0.2)
        except Empty:
            return
        block_penalty = self.chain.block_penalty(block)
        if (
            self.__best_block_penalty is None
            or block_penalty < self.__best_block_penalty
        ):
            self.__current_best_block = block
            self.__best_block_penalty = block_penalty

    def _reset(self):
        self.__current_best_block = None
        self.__best_block_penalty = None

    def _add_new_block(self):
        if self.__current_best_block is not None:
            logger.info(f"Adding block index: {self.__current_best_block.index} hash: {self.__current_best_block.hash}")
            self.chain.link_new_block(
                self.__current_best_block, _i_know_what_i_doing=True
            )
        self._reset()

    def run(self):
        while not self.__stop:
            if self.__pause:
                sleep(0.2)
                continue
            self._check_block()
            if int(time()) % Config.new_block_interval == 0:
                self._add_new_block()

    def stop(self):
        self.__stop = True

    def pause(self):
        self.__pause = True

    def unpause(self):
        self.__pause = False
