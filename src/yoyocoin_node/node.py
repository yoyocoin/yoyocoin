from loguru import logger

from p2p_network import Node, Connection, Message
from blockchain import Chain, ChainSummery
from blockchain.block import Block
from blockchain.exceptions import ValidationError

from .ipfs import Ipfs
from .coin_protocols import TransactionProtocol, BlockProtocol, ChainSummeryProtocol


class YoyocoinNode(Node):
    def __init__(self, host: str):
        self.__class__.LISTEN_HOST = host  # for Local testing
        self.protocols = [
            TransactionProtocol(self),
            BlockProtocol(self),
            ChainSummeryProtocol(self),
        ]
        self.ipfs = Ipfs.get_instance()
        super().__init__(protocols=self.protocols)

    @property
    def blockchain(self) -> Chain:
        return Chain.get_instance()

    def on_message(self, message):
        sender, data = message
        print(sender, data)

    def on_new_connection(self, connection: Connection):
        pass

    def on_connection_closed(self, connection: Connection):
        pass

    def broadcast_transaction(self, transaction_dict: dict):
        self.broadcast(TransactionProtocol.create_broadcast_transaction_message(transaction_dict))

    def broadcast_candidate_block(self, block_dict: dict):
        self.broadcast(BlockProtocol.create_broadcast_block_message(block_dict))

    def request_chain_summery(self):
        """
        Request chain summery
        chain summery contains:
            blocks hash's and cid's
            chain score
        :return: chain diff start index, chain summery, block cid's, peer address (that send the summery)
        """
        best_summery = None
        best_cids = None
        sender_address = None
        for address in self.connected_peers:
            connection = self.get_connection(address)
            summery_bytes = connection.get(ChainSummeryProtocol.create_chain_summery_request_message().to_bytes())
            summery_message = Message.from_bytes(summery_bytes)
            summery_dict = summery_message.dict_message["summery"]
            cids = summery_message.dict_message["cids"]
            summery = ChainSummery.from_dict(summery_dict)
            if best_summery is None:
                best_summery = summery
                best_cids = cids
                sender_address = address
            else:
                if summery > best_summery:
                    best_summery = summery
                    best_cids = cids
                    sender_address = address
        if best_summery is None:
            return None
        start_diff = self.blockchain.summery.diff(best_summery)
        return start_diff, best_summery, best_cids, sender_address

    def sync(self):
        """
        Sync chain with best chain found from peers
        1. load all the peers chains
        2. choose the best one
        3. update and validate new chain
        4. if new chain is invalid block sending peer and sync again
        :return: None
        """
        try:
            self.blockchain.next_block_chooser.pause()
            summery_diff = self.request_chain_summery()
            if summery_diff is None:
                return
            start_diff, summery, cids, peer_address = summery_diff
            logger.info(f"Start sync process with expected penalty: {summery.penalty} length: {summery.length}")
            sync_chain = Chain(_i_know_what_i_doing=True)
            for cid in cids:
                block_dict = self.ipfs.load_cid(cid)
                block = Block.from_dict(block_dict)
                try:
                    sync_chain.link_new_block(_i_know_what_i_doing=True, block=block)
                except ValidationError:
                    # TODO: block peer address
                    raise
            print(sync_chain.summery.length, sync_chain.summery.penalty, self.blockchain.summery.length, self.blockchain.summery.penalty)
            if sync_chain.summery > self.blockchain.summery:
                Chain.update_chain(sync_chain)
                logger.success(f"Chain synced!")
        finally:
            self.blockchain.next_block_chooser.unpause()
