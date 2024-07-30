"""REST API client module for wildberries"""
from __future__ import annotations

from requests import PreparedRequest, Response

from aftafa.client.baseclient import BaseClient, BaseAuth
from aftafa.client.ozon.supplier import OzonSellerSupplier


BASE_URL: str = "https://api-seller.ozon.ru"


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
