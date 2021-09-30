from p2p_network import Node, Connection


class YoyocoinNode(Node):
    def __init__(self, host: str):
        self.__class__.LISTEN_HOST = host  # for Local testing
        super().__init__()

    def on_message(self, message):
        sender, data = message
        print(sender, data)

    def on_new_connection(self, connection: Connection):
        pass

    def on_connection_closed(self, connection: Connection):
        pass
