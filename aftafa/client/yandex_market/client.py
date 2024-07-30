"""REST API client module for wildberries"""
import json
import os
from typing import Literal

import requests
from requests.adapters import HTTPAdapter

from aftafa.common.config import Config


BASE_URL: str = "https://api.partner.market.yandex.ru"
cfg: Config = Config()
META = cfg._get_meta_credentials_file('YA')


class ClientSupplier:
    """Class represents a supplier as a legal name / account registered in the system"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.id: str = META["suppliers"][name]["campaign_id"]
        self.client_id: str = META["suppliers"][name]["client_id"]
        self.token: str = META["suppliers"][name]["token"]
        self.business_id: int = META["suppliers"][name]["business_id"]


class ClientSession(requests.Session):
    """This class is a prototype for all the fetchers, we implement them as a Sessions"""

    def __init__(self, supplier: ClientSupplier) -> None:
        requests.Session.__init__(self)
        self.supplier = supplier
        self.params: dict[str, str] = {}
        self.mount("https://", HTTPAdapter(max_retries=2))
        self.headers.update(
            {
                "Authorization": f"OAuth oauth_token={supplier.token}, oauth_client_id={supplier.client_id}",
                "content-type": "application/json",
            }
        )


class ClientMethod:
    """Class for constructing methods a k a endpoints"""

    def __init__(self, api_method: Literal["GET", "POST"], api_endpoint: str) -> None:

        self.api_method = api_method
        self.api_endpoint = api_endpoint
        self.url = BASE_URL + api_endpoint
