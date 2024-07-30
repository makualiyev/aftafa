import os
import json

from requests import Session

from aftafa.common.config import Config


cfg: Config = Config()

META = cfg._get_meta_credentials_file('SBERMM')
BASE_URL = 'https://partner.sbermegamarket.ru'
PRIVATE_MERCHANTS = META['meta']['private_merchants']

class ApiClient:

    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.merchants = {                              # or PRIVATE MERCHANTS
            'SAMSUNG': 1
        }
        self.session_id: str = ""
        self.headers = {
           'authority': 'partner.sbermegamarket.ru',
           'accept': 'application/json',
           'accept-language': 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,az;q=0.6',
           'content-type': 'application/json',
           'origin': BASE_URL,
           'referer': BASE_URL + '/auth',
           'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"Windows"',
           'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'same-origin',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'
        }
        self.payload = {
                        'meta': {
                            'from': 'mui-router',
                        },
                        'data': {
                            'login': META['users'][self.supplier]['login'],
                            'password': META['users'][self.supplier]['password'],
                        },
                    }


    def authorize(self) -> Session:
        sesh = Session()
        sesh.headers.update(self.headers)
        with sesh.post(
                    url=(BASE_URL + '/api/merchantUIService/v1/securityService/session/start'),
                    json=self.payload
                ) as response:
            if response.status_code == 200:
                sesh.session_id = response.json()['data']['sessionId']
            else:
                print(f'Failed authorization -> {response.content}')

        return sesh
    
    def change_merchant(self, sesh: Session, merchant: str) -> Session:
        merchant_id = self.merchants.get(merchant)
        
        with sesh.post(
            url=(BASE_URL + '/api/merchantManagerUIService/v1/securityService/redirectToken/create'),
            json={"meta":{"from":"mui-router"},"data":{"merchantId":merchant_id,"sessionId":sesh.session_id}}
        ) as response:
            if response.status_code == 200:
                refresh_token: str = response.json()['data']['token']
            else:
                print(f"Couldn't create a redirect token for this merchant {merchant}")
                return None
        with sesh.post(
            url=(BASE_URL + '/api/merchantManagerUIService/v1/securityService/redirectToken/check'),
            json={"meta":{"from":"mui-router"},"data":{"token": refresh_token}}
        ) as response:
            if response.status_code == 200:
                with sesh.post(
                    url=(BASE_URL + '/api/market/v2/securityService/user/impersonate'),
                    json={"meta":{"from":"mui-router"},"data":{"sessionId":sesh.session_id,"merchantId":merchant_id}}
                ) as response:
                    if response.status_code == 200:
                        sesh._merchant_id = merchant_id
                        return sesh
                    else:
                        print(f"Couldn't impersonate and redirect to this merchant {merchant}")
                        return None
            else:
                print(f"Couldn't check a redirect token for this merchant {merchant}")
                return None
            



class MPmethod(object):
    def __init__(self, api_method : str, api_endpoint : str, api_engine : str = 'apiseller') -> None:
        self.api_method = api_method
        self.api_endpoint = api_endpoint
        self.url = BASE_URL + api_endpoint