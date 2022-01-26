from pathlib import Path


HEARTBEAT_RATE = 1  # Seconds

CONNECT_EVERY_X_HEARBEATS = 10
BROADCAST_ADDR_EVERY_X_HEARTBEATS = 20

ROOT = Path(__file__).parent.parent
BOOTSTRAP_LIST = str(ROOT / "config" / "bootstrap.list")

CLIENT_RECV_BATCH = 50000
SERVER_RECV_BATCH = 2048
MESSAGE_DELIMITER = b"%99"
