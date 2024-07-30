import json
import os
import requests
from collections import Counter
from typing import Union, Iterator

from aftafa.common.config import Config
from aftafa.utils.helpers import bcolors


BASE_URL = "https://api-seller.ozon.ru"
BASE_ACC_URL = "https://seller.ozon.ru"
BASE_PERF_URL = "https://performance.ozon.ru:443"
cfg: Config = Config()
META = cfg._get_meta_credentials_file('OZ')


class MPsupplier(object):
    """This class represents a user for authenticating to the External OZON API via credentials
    which are stored in a JSON config file (in our case it's meta.json). It has appropriate fields which resembles
    the exact ones required to pass in headers of requests to the service. Those fields are fetched automatically
    from the meta file if the name of a supplier (OZON account) is provided.
    - name : str = The name of an OZON account."""
    def __init__(self, name : str) -> None:
        self.name : str = name
        self.id : str = META['suppliers'][name]['client_id'] # TODO : change id to client id as id is a keyword in python
        self.token : str = META['suppliers'][name]['api_key']
        self.headers : dict =  {
                "Api-Key": self.token,
                "Client-Id": self.id,
                "Content-Type": "application/json"
              }


class MPmethod(object):
    def __init__(self, api_method : str, api_endpoint : str, api_engine : str = 'apiseller') -> None:
        self.api_method = api_method
        self.api_endpoint = api_endpoint
        if api_engine == 'account':
            self.url = BASE_ACC_URL + api_endpoint
        elif api_engine == 'performance':
            self.url = BASE_PERF_URL + api_endpoint
        else:
            self.url = BASE_URL + api_endpoint
    

class MPServiceAccount(object):
    """This object represents service accounts that interact with performance API"""

    def __init__(self, name: str) -> None:
        self.name : str = name
        self.id : str = META['suppliers'][name]['client_id']
        self.container : list = META['suppliers'][name]['performance']
        self.headers : dict =  {
                "Content-Type" : "application/json",
                "Accept" : "application/json",
                "Connection" : "keep-alive"
              }
        
    def get_session_generator(self) -> Iterator[requests.Session]:
        """method to authorize into performance accounts"""
        def get_auth_session(num : int) -> str:
            sesh = MPsesh(supplier=self)
            sesh.headers.update(self.headers)
            payload = {
                "client_id": self.container[num]["client_id"],
                "client_secret": self.container[num]["client_secret"],
                "grant_type" : "client_credentials"
            }
            with sesh.post(url=BASE_PERF_URL + "/api/client/token", json=payload) as response:
                if response.status_code == 200:
                    sesh.headers['Token'] = response.json()['access_token']
                    return sesh
                print(f"It failed for this one {self.name} with this {response.content}")

        for i in range(len(self.container)):
            yield get_auth_session(i)


class MPsesh(requests.Session):
    """This class is a prototype for all the fetchers, we implement them as a Sessions"""
    def __init__(self, supplier : Union[MPsupplier, MPServiceAccount]) -> None:
        requests.Session.__init__(self)
        self.supplier = supplier
        self.headers.update(supplier.headers)



class UtlPostingReturn:
    """this util class is for representing postings in a tree-like structure"""
    def __init__(self, order_id : str, posting_number : str) -> None:
        self.order_id = order_id
        self.posting_number = posting_number
        self.skus = []

    @property
    def skus_container(self) -> dict:
        return dict(Counter(self.skus))

    def __repr__(self) -> str:
        return f"Posting({self.posting_number}) with skus : {Counter(self.skus)}"
                        
class UtlOrderReturn:
    """this util class is for representing orders in a tree-like structure which makes it easier to
    inspect and compare while checking returns for postings. FYI - many postings change their numbers as soon as they are cancelled and etc"""
    def __init__(self, order_id : str) -> None:
        self.order_id = order_id
        self.postings = {}

    def add_postings(self, return_entry : dict) -> None:
        if post_in_order := self.postings.get(return_entry['posting_number']):
            post_in_order.skus.append(return_entry['sku'])
        else:
            posting = UtlPostingReturn(order_id=self.order_id, posting_number=return_entry['posting_number'])
            posting.skus.append(return_entry['sku'])
            self.postings[posting.posting_number] = posting

    @property
    def view_skus(self) -> dict:
        view = {}
        for posting in self.postings:
            for sku in self.postings[posting].skus:
                view[sku] = posting
        return view

    @property
    def skus_container(self) -> dict:
        view = []
        for posting in self.postings:
            view.extend(self.postings[posting].skus)
        return dict(Counter(view))
        
    def is_equal(self, other_order) -> bool:
        """This method is used to compare return order trees"""
        conditions = [
            self.order_id == other_order.order_id,
            not bool(set(other_order.view_skus.keys()) - set(self.view_skus.keys()))
        ]
        return all(conditions)

    def __repr__(self) -> str:
        return f"Order({self.order_id}) : {self.postings}"