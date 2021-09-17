import json
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.util.retry import Retry


class Node:
    def __init__(self):
        self.ipfs_api_base_url = "http://127.0.0.1:5001/api/v0/"
        self.ipfs_session = self.setup_ipfs_session()
        self.ipfs_version = self.load_ipfs_version()

    def setup_ipfs_session(self):
        ipfs_session = requests.Session()
        retries = Retry(total=15, backoff_factor=1)
        ipfs_session.mount('http://', HTTPAdapter(max_retries=retries))
        return ipfs_session

    def load_ipfs_version(self) -> dict:
        return self.ipfs_session.post(urljoin(self.ipfs_api_base_url, "version"), params={"all": True}).json()

    def load_cid(self, cid: str) -> dict:
        return self.ipfs_session.post(urljoin(self.ipfs_api_base_url, "block/get"), params={"arg": cid}).json()

    def create_cid(self, data: dict) -> str:
        bytes_data = json.dumps(data).encode()
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "block/put"),
            files={"content": bytes_data}
        ).json()

    def publish_to_topic(self, topic: str, data: dict):
        json_data = json.dumps(data)
        return self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "pubsub/pub"),
            params={"arg": [topic, json_data]}
        ).text

    def subscribe_to_topic(self, topic: str):
        subscribe_stream = self.ipfs_session.post(
            urljoin(self.ipfs_api_base_url, "pubsub/sub"),
            params={"arg": topic},
            stream=True
        )
        return subscribe_stream
