"""REST API client module for wildberries"""
from __future__ import annotations
import json

from requests import PreparedRequest, Response

from aftafa.common.config import Config
from aftafa.client.baseclient import BaseClient, BaseAuth


BASE_URL: str = "https://api-seller.ozon.ru"

class OzonSellerSupplier:
    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.meta = None
        self._get_meta_info()

    def _get_meta_info(self) -> None:
        cfg = Config()
        with open(cfg._get_meta_credentials_file(channel='OZ'), 'rb') as f:
            meta_dump = json.load(f)
        self.meta = meta_dump.get('suppliers').get(self.supplier)

    @property
    def info(self) -> dict[str, str]:
        return {
            'client_id': self.meta.get('client_id'),
            'api_key': self.meta.get('api_key')
        }

    def _get_api_server(self, server: str) -> str:
        pass


class OzonSellerClient(BaseClient):
    def __init__(self, supplier: str, baseurl: str = BASE_URL) -> None:
        super().__init__(baseurl=baseurl)
        self.supplier = supplier
        self.supplier_id = int(OzonSellerSupplier(supplier=supplier).info['client_id'])
        self.headers.update({
            "Content-Type" : "application/json"
        })

    def request(self, method, url, *args, **kwargs) -> Response:
        return super().request(
            method,
            url,
            *args,
            **kwargs,
            **{
                "auth": OzonSellerClientAuth(supplier=self.supplier)
            }
        )


class OzonSellerClientAuth(BaseAuth):
    def __init__(self, supplier: str) -> None:
        super().__init__()
        self.supplier = supplier

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers['Client-Id'] = OzonSellerSupplier(supplier=self.supplier).info['client_id']
        r.headers['Api-Key'] = OzonSellerSupplier(supplier=self.supplier).info['api_key']
        return r
