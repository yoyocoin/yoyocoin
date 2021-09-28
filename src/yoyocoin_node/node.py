from p2p_network import Node


class YoyocoinNode:
    def __init__(self, host: str):
        self.node = Node(on_message=self.on_message, listen_host=host, max_outbound_connections=2)

    def on_message(self, message):
        sender, data = message
        print(sender, data)

    def start(self):
        self.node.start()
