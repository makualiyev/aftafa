from __future__ import annotations
import json

import requests

from aftafa.common.config import Config


cfg: Config = Config()

META_DIR = cfg._get_meta_credentials_file('DIADOC')
BASE_URL = 'https://diadoc-api.kontur.ru/'

class DiadocMetaRegistry:
    META_DIR = r'E:/shoptalk/local_/meta/meta_diadoc.json'

    def __init__(self) -> None:
        self._meta = self._init_meta()

    def _init_meta(self) -> dict[str, str]:
        with open(META_DIR, 'rb') as f:
            meta_dict: dict[str, str] = json.loads(f.read())
        return meta_dict
        
    def update_meta(self, new_token: str) -> None:
        self._meta['auth_token'] = new_token
        with open(META_DIR, 'w') as f:
            f.write(json.dumps(self._meta))
        self._meta = self._init_meta()



class DiadocClient(requests.Session):
    """This class is for interacting with a backend API directly from the site. 
    UNSTABLE"""
    def __init__(
        self
    ) -> None:
        self._registry = DiadocMetaRegistry()
        requests.Session.__init__(self)
        self.mount('https://', requests.adapters.HTTPAdapter(max_retries=2))
        self.base_url = BASE_URL
        self.headers.update({
            'Host': 'diadoc-api.kontur.ru',
            'Authorization': f"DiadocAuth ddauth_api_client_id={self._registry._meta['token']},ddauth_token={self._registry._meta['auth_token']}",
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        })

    def _update_meta(self, new_token: str) -> None:
        self._registry.update_meta(new_token=new_token)
        self.headers['Authorization'] = f"DiadocAuth ddauth_api_client_id={self._registry._meta['token']},ddauth_token={new_token}"


    def authorize(self) -> DiadocClient | None:
        saved_auth_token = self._registry._meta['auth_token']
        with self.get('https://diadoc-api.kontur.ru/GetMyOrganizations') as response:
            if response.status_code == 200:
                return self
            else:
                print(f"Refreshing auth token - {response.status_code}")
        with self.post(
                            url=BASE_URL + '/V3/Authenticate',
                            params={
                                'type':'password'
                            },
                            json={
                                'login': self._registry._meta['login'],
                                'password': self._registry._meta['password']
                            },
                            timeout=45
                        ) as response:
            if response.status_code == 200:
                new_token = response.content.decode()
                self._update_meta(new_token=new_token)
                return self
            else:
                print(f"Couldn't update refresh token with this status code {response.status_code} \n and content -> {response.content}")

    # def request(self, *args, **kwargs) -> requests.Response:
    #     return super().request(*args, **kwargs)
    

