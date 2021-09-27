import json
from urllib.parse import urljoin

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.util.retry import Retry  # type: ignore

from p2p_network.config import Config


class Ipfs:
    def __init__(self):
        self.ipfs_api_base_url = Config.ipfs_node_base_url
        self.timeout = Config.ipfs_request_timeout
        self.ipfs_session = self.setup_ipfs_session()
        self.ipfs_version = self.load_ipfs_version()

    def setup_ipfs_session(self):
        ipfs_session = requests.Session()
        retries = Retry(total=15, backoff_factor=1)
        ipfs_session.mount('http://', HTTPAdapter(max_retries=retries))
        return ipfs_session

    def load_ipfs_version(self) -> dict:
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "version"),
            params={"all": True},
            timeout=self.timeout,
        ).json()

    def load_cid(self, cid: str) -> dict:
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "block/get"),
            params={"arg": cid},
            timeout=self.timeout,
        ).json()

    def create_cid(self, data: dict) -> str:
        bytes_data = json.dumps(data).encode()
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "block/put"),
            files={"content": bytes_data},
            timeout=self.timeout,
        ).json()
