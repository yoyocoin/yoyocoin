import random
from os import path
from typing import List, Tuple, Callable, Dict

import requests

from .config import Config

NodeAddress = Tuple[str, int]  # ip, port
Callback = Callable[[Dict], None]


class Node:
    def __init__(self, on_network_broadcast: Callback):
        self._on_network_broadcast_callback: Callback = on_network_broadcast
        self._connected_nodes: List[NodeAddress] = []
        self._initialized: bool = False

    def _load_bootstrap_nodes(self) -> List[NodeAddress]:
        """
        load bootstrap nodes from disk or hardcoded list:
        if bootstrap nodes file exists load it else return hardcoded list
        :return: bootstrap nodes address list
        """
        if path.exists(Config.bootstrap_list_file_path):
            with open(Config.bootstrap_list_file_path) as bootstrap_file:
                file_bootstrap_list = bootstrap_file.read()
            if file_bootstrap_list:
                return [
                    (node_address.split(":")[0], int(node_address.split(":")[1]))
                    for node_address in file_bootstrap_list.split("\n")
                ]
        return Config.bootstrap_nodes_address

    def _load_nodes_list_from_bootstrap_node(self, node_address: NodeAddress) -> List[NodeAddress]:
        """
        Get nodes list from bootstrap node with http request
        :param node_address: the bootstrap node address
        :return: list of currently active nodes
        """
        response = requests.get(
            f"http://{node_address[0]}:{node_address[1]}/api/v1/active_nodes_list",
            params={"max": Config.bootstrap_list_request_max},
            timeout=Config.bootstrap_request_timeout
        )
        return response.json()["nodes"]

    def _connect_to_node(self, node_address: NodeAddress) -> bool:
        """
        Connect to node server
        :param node_address: the node address we are connecting to
        :return: True for successful connection else False
        """
        response = requests.post(
            f"http://{node_address[0]}:{node_address[1]}/api/v1/connect",
            timeout=Config.node_connect_request_timeout
        )
        return response.status_code == 200 and response.json()["connected"] is True

    def _connect_to_network(self) -> List[NodeAddress]:
        """
        Connect to <max outbound> nodes
        1. load bootstrap nodes
        2. get list of nodes
        3. select <max outbound> random nodes
        4. connect to nodes
        :return: list of outbound connected nodes
        """
        bootstrap_nodes_address = self._load_bootstrap_nodes()
        all_active_nodes = set()
        for bootstrap_node_address in bootstrap_nodes_address:
            active_nodes_address = self._load_nodes_list_from_bootstrap_node(bootstrap_node_address)
            all_active_nodes |= set(active_nodes_address)
        margin = 5
        chosen_outbound_nodes = random.choices(list(all_active_nodes), k=Config.max_outbound_connections+margin)
        connected_nodes = []
        for outbound_node_address in chosen_outbound_nodes:
            connected = self._connect_to_node(outbound_node_address)
            if connected:
                connected_nodes.append(outbound_node_address)
            if len(connected_nodes) >= Config.max_outbound_connections:
                break
        return connected_nodes

    def broadcast(self, data: dict) -> bool:
        """
        Broadcast the data to the network
        :param data:
        :return:
        """
        pass

    def _initialize(self):
        """
        Initialize node
        1. connect to outbound nodes
        2. listen to network broadcast (run http server)
        :return:
        """
        pass

    def start(self):
        """
        Start the node:
        connect to nodes and listen for network broadcast
        """
        pass
