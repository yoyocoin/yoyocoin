import os
from time import sleep

from blockchain import Chain, Config, Actor
from netp2p import Node, messages


class Manager:
    def __init__(self, port: int = 1875) -> None:
        self.blockchain = Chain.get_instance()
        self.actor = Actor(os.getenv("WALLET_SECRET_KEY", f"test-{port}"))
        self.node = Node(self.blockchain, os.getenv("PORT", port))  # TODO: remove magic number
    
    def run(self):
        self.node.start()
        while True:
            sleep(Config.new_block_interval)
            
            block = self.actor.forge_block()
            self.blockchain.add_block(block.to_dict())
            self.node.broadcast(messages.NewBlock(block.to_dict()))
    