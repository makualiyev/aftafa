# """REST API client module for wildberries"""
# from __future__ import annotations
# import json
# import os
# from collections import Counter
# from typing import Literal, Union, Iterator

# import requests
# from requests import PreparedRequest, Response
# from requests.adapters import HTTPAdapter

# from sennetl.clients.baseclient import BaseClient, BaseAuth
# from sennetl.clients.wildberries.supplier import WildberriesSupplier



# BASE_URL: str = "https://suppliers-api.wildberries.ru"                   # this one is called "new API" and mainly used to work with FBS
# BASE_STATS_URL: str = "https://statistics-api.wildberries.ru"           # this one contains important analytical data
# BASE_SITE_URL: str = 'https://seller.wildberries.ru'


# class WildberriesClient(BaseClient):
#     def __init__(self, supplier: str, baseurl: str = '') -> None:
#         super().__init__(baseurl=baseurl)
#         self.supplier = supplier
#         self.headers.update({
#             "Content-Type" : "application/json",
#             "Accept" : "application/json",
#             "Authorization": ""
#         })

#     def request(self, method, url, *args, **kwargs) -> Response:
#         return super().request(method, url, *args, **kwargs)


# class WildberriesClientAuth(BaseAuth):
#     def __init__(self, supplier: str) -> None:
#         super().__init__()
#         self.supplier = supplier

#     def __call__(self, r: PreparedRequest) -> PreparedRequest:
#         r.headers['Authorization'] = WildberriesSupplier(supplier=self.supplier).info['jwt_token__stats']
#         return r

