import typing as tp
import json
from urllib.parse import urljoin

import requests

from aftafa.common.config import Config



cfg: Config = Config()
META = cfg._get_meta_credentials_file('MPSTATS')
BASE_URL = 'https://mpstats.io/api/'

class MPSClient(requests.Session):
    """This class is for interacting with a backend API directly from the site. 
    UNSTABLE"""
    def __init__(
        self
    ) -> None:
        requests.Session.__init__(self)
        self.mount('https://', requests.adapters.HTTPAdapter(max_retries=2))
        self.base_url = BASE_URL
        self.headers.update(
            {
                'X-Mpstats-TOKEN': META['token'],
                'Content-Type': 'application/json'
            }
        )

    def request(self, method: str, url: str | bytes, *args, **kwargs) -> requests.Response:
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)
        