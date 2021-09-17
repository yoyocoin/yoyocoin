import json
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.util.retry import Retry

from .config import Config


class Node:
    def __init__(self):
        self.ipfs_api_base_url = Config.ipfs_node_base_url
        self.timeout = Config.request_timeout
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

    def publish_to_topic(self, topic: str, data: dict):
        json_data = json.dumps(data)
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "pubsub/pub"),
            params={"arg": [topic, json_data]},
            timeout=self.timeout,
        ).text

    def subscribe_to_topic(self, topic: str):
        subscribe_stream = self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "pubsub/sub"),
            params={"arg": topic},
            stream=True,
            timeout=self.timeout,
        )
        return subscribe_stream
