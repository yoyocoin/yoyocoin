__all__ = ["Config"]


class Config:
    bootstrap_list_file_path = "config/bootstrap.list"

    max_outbound_connections = 16
    max_inbound_connections = 32

    bootstrap_nodes_address = [("127.0.0.2", 6001)]
    bootstrap_list_request_max = 200
    bootstrap_request_timeout = 2  # Seconds

    node_version = "0.0.1"
    node_listen_port = 6001
    node_listen_host = "0.0.0.0"

    socket_connect_timeout = 2  # Seconds
    socket_request_timeout = 5  # Seconds
    socket_max_buffer_size = 1024 * 1024 * 2  # 2Mb

    heartbeat_interval = 1
