__all__ = ["Config"]


class Config:
    ipfs_node_base_url = "http://127.0.0.1:5001/api/v0/"
    ipfs_request_timeout = 5  # Seconds

    bootstrap_list_file_path = "config/bootstrap.list"

    max_inbound_connections = 10
    max_outbound_connections = 10

    bootstrap_nodes_address = [("154.13.45.7", 6001)]
    bootstrap_list_request_max = 200
    bootstrap_request_timeout = 2  # Seconds

    node_connect_request_timeout = 5  # Seconds
