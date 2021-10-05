import json
from urllib.parse import urljoin

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.util.retry import Retry  # type: ignore

from loguru import logger


class Ipfs:
    BASE_URL = "http://127.0.0.1:5001/api/v0/"
    REQUEST_TIMEOUT = 5

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls(_i_know_want_i_doing=True)
        return cls._instance

    def __init__(self, _i_know_want_i_doing: bool = False):
        if not _i_know_want_i_doing:
            raise RuntimeError("Cant init singleton. use get_instance class method")
        self.timeout = self.REQUEST_TIMEOUT
        self.ipfs_session = self.setup_ipfs_session()
        self.ipfs_version = self.load_ipfs_version()

    def setup_ipfs_session(self):
        ipfs_session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        ipfs_session.mount('http://', HTTPAdapter(max_retries=retries))
        return ipfs_session

    def load_ipfs_version(self) -> dict:
        logger.info("Loading ipfs node version")
        return self.ipfs_session.post(
            urljoin(self.BASE_URL, "version"),
            params={"all": True},
            timeout=self.timeout,
        ).json()

    def load_cid(self, cid: str) -> dict:
        return self.ipfs_session.post(
            urljoin(self.BASE_URL, "block/get"),
            params={"arg": cid},
            timeout=self.timeout,
        ).json()

    def create_cid(self, data: dict) -> str:
        bytes_data = json.dumps(data).encode()
        return self.ipfs_session.post(
            urljoin(self.BASE_URL, "block/put"),
            files={"content": bytes_data},
            timeout=self.timeout,
        ).json()["Key"]
