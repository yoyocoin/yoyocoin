from threading import Thread
from time import time
from queue import Queue, Empty

from .config import Config
from .block import Block


class NextBlockChooser(Thread):
    def __init__(self, chain):
        super().__init__(daemon=True)
        self.chain = chain

        self.blocks_queue = Queue()

        self.__current_best_block = None
        self.__best_block_penalty = None
        self.__stop = False

    def scan_block(self, block: Block):
        self.chain.validate_block(block)
        self.blocks_queue.put(item=block)

    def _check_block(self):
        try:
            block: Block = self.blocks_queue.get(timeout=1)
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
            self.chain.link_new_block(
                self.__current_best_block, _i_know_what_i_doing=True
            )
        self._reset()

    def run(self):
        while not self.__stop:
            self._check_block()
            if int(time()) % Config.new_block_interval == 0:
                self._add_new_block()

    def stop(self):
        self.__stop = True
