"""REST API client module for wildberries"""
from __future__ import annotations
import json
import os
from collections import Counter
from typing import Literal, Union, Iterator

import requests
from requests.adapters import HTTPAdapter

from aftafa.common.config import Config


BASE_URL: str = "https://suppliers-api.wildberries.ru"                   # this one is called "new API" and mainly used to work with FBS
BASE_STATS_URL: str = "https://statistics-api.wildberries.ru"           # this one contains important analytical data
BASE_SITE_URL: str = 'https://seller.wildberries.ru'
BASE_PRICE_URL: str = 'https://discounts-prices-api.wb.ru'
cfg: Config = Config()
META = cfg._get_meta_credentials_file('WB')


class ClientSupplier:
    """Class represents a supplier as a legal name / account registered in the system"""
    def __init__(self, name: str) -> None:
        self.name = name
        self.id: str = META['suppliers'][name]['supplier_id']
        self.token: str = META['suppliers'][name]['token']
        self.api_key: str = META['suppliers'][name]['api_key']
        self.jwt_tokens: dict[str, str] = META['suppliers'][name]['jwt_tokens']


class ClientDirectSession(requests.Session):
    """This class is for interacting with a backend API directly from the site. 
    UNSTABLE"""
    def __init__(
        self,
        supplier: ClientSupplier,
        wildauthnewv3: str = META['wildauthnewv3']
    ) -> None:
        requests.Session.__init__(self)
        self.supplier = supplier
        self.wildauthnewv3 = wildauthnewv3
        self.params: dict[str, str] = {}
        self.mount('https://', HTTPAdapter(max_retries=2))
        self.headers.update(
            {
                "Content-type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            }
        )
        self.cookies.update({
            'WILDAUTHNEW_V3': wildauthnewv3
        })

    def authorize(self) -> bool:
        """
        Authorizes using wildauthnewv3 token from customer sign in
        """
        with self.post(
                    url=(BASE_SITE_URL + '/passport/api/v2/auth/wild_v3_upgrade'), 
                    json={'device': 'Windows'}
            ) as response:
            if response.status_code != 200:
                print(f'Failed authorizing via WILDAUTHNEWv3 :( here is the status -> {response.status_code} \
                    \n and response -> {response.content}')
                return False
            response_cookies: str = response.headers.get('Set-Cookie')
            wb_token_split: list[str] = response_cookies.split(';')[0].split('=')
            if len(wb_token_split) == 2 and (wb_token_split[0] == 'WBToken'):
                wb_token = wb_token_split[1]
            self.cookies.update({
                'WBToken': wb_token,
                'x-supplier-id': self.supplier.id,
                'x-supplier-id-external': self.supplier.id
            })
            return self

    def change_supplier(self, supplier: str) -> bool:
        self.supplier = ClientSupplier(name=supplier)
        self.cookies.update({
                'x-supplier-id': self.supplier.id,
                'x-supplier-id-external': self.supplier.id
        })
        return self


class ClientDirectSessionV2(requests.Session):
    """This class is for interacting with a backend API directly from the site. 
    UNSTABLE"""
    def __init__(
        self,
        supplier: ClientSupplier,
        wildauthnewv3: str = META['wildauthnewv3']
    ) -> None:
        requests.Session.__init__(self)
        self.supplier = supplier
        self.wildauthnewv3 = wildauthnewv3
        self.params: dict[str, str] = {}
        self.mount('https://', HTTPAdapter(max_retries=2))
        self.default_headers = {
            "Cookie": f"__bsa=basket-ru-23; _ym_uid=167333934632215979; _ga=GA1.2.678603094.1688646291; _ga_EVJH2CFDRY=GS1.1.1688646291.1.0.1688646293.0.0.0; external-locale=ru; _ym_d=1693486717; enabled_feature_version=2; _wbauid=7809370961701797193; BasketUID=516f163bb2ca41c0a943bb11d234fd37; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UrQGgmYEdaKDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwZE3l0K08ODWQ/RWllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVgSFEZd2I/ezFWN0RzZys0EnMIHkofT0kwQn4rNH9mX19vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwdYUliJ0NcTwonHg1pN2wXPHVlLwkxLGJ5MVIvE0tsGA==AHvJaQ==; x-supplier-id={META['suppliers'][supplier.name]['supplier_id']}; x-supplier-id-external={META['suppliers'][supplier.name]['supplier_id']}; ___wbu=ad213d68-eb6e-479e-923a-0aed27d24eaa.1704815201; WBToken=AqvfjQys6pHbDKy-pdwMU9GTkRGuIHk2A_GR-LnqPNsejuQCdzm6-eqOyFf5vB2zZ8ijReew-DoPF6_2VEBcdiQj1H3DIZk_VAeEXVt5g9ZNyFJwSAtgbdhPYkb8F3LRn6zI; current_feature_version=70570136-C575-44F7-99E9-7C9727AA8E51; wbx-validation-key=3d4eb68c-af93-4303-89cc-391174d0bdbd; WBTokenV3=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDY3NzkxMDgsInZlcnNpb24iOjIsInVzZXIiOiIyNTM5MTAxOSIsInNoYXJkX2tleSI6IjE5IiwiY2xpZW50X2lkIjoic2VsbGVyLXBvcnRhbCIsInNlc3Npb25faWQiOiJlMzE5OGI2YTE4YjY0YTBmOTcyZDkwMTkyNzI2ZDBkNiIsInVzZXJfcmVnaXN0cmF0aW9uX2R0IjoxNjc0MDcxNjkxLCJ2YWxpZGF0aW9uX2tleSI6Ijk0ZDVhYmEyNTkzZDQyMDViNTE4Nzk2Yjc5MGFhNWE4MzU2OGMxNmUwMzM5ZTUyMGNiZjAwOTdlMzBlODg5N2MiLCJwaG9uZSI6Inh2ZFNzS3Q3TkxrWS9QMVpPQkVEc0E9PSJ9.Pd85G00CCIjUAcLFRZaBkGi0HeB-iWKVW4h7deeOvEy_e03YqHndVJ2F-uljMCQzbR0M_tehXq20wQ8-Tj_Rg9FexYEyhDP76kGEGujnbJFTKKJk_21ZJyIECAe2JCGSnaGqPoH_qQy5hHso4z_CP0xRs5RGd6mxPF8kHqYILo3Qk45NUWsStYZv-eOhCmXIzDGblX9lsIQE7O_BGiQDtmWsMRna6YEEHQ8Xh0fNrrF1CsX4hhMXcgGjVRDanrN-hTpSzJqmrzu4wTH5FtQxenol8402NdTv_buLCTV_tIBnqPIUh1QuOjO5ic-Bc7pKUXuGA4S7BydI9Cfu25gVew; locale=ru; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UrQGgmYEdaKDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwZE3l0K08ODWQ/RWllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVgSFEZd2I/ezFWN0RzZys0EnMIHkofT0kwQn4rNH9mX19vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwdYUliJ0NcTwonHg1pN2wXPHVlLwkxLGJ5MVIvE0tsGA==AHvJaQ==; cfidsw-wb=CVYggxUtodFn8HLeYIXTmK7L8TJPIB4cOaIah7E4Vdrqb7S62hi4ufFboced9mjQmXfQjPKHeRJRS5pXmhOYoRSFkxAYyFUzILKcPLUi6QfLBFdxD/AOsCHE67RrSklDhA1zERmbQmE8VK3gLdREJUsx+9s78HXeeHGmtVNk; cfidsw-wb=CVYggxUtodFn8HLeYIXTmK7L8TJPIB4cOaIah7E4Vdrqb7S62hi4ufFboced9mjQmXfQjPKHeRJRS5pXmhOYoRSFkxAYyFUzILKcPLUi6QfLBFdxD/AOsCHE67RrSklDhA1zERmbQmE8VK3gLdREJUsx+9s78HXeeHGmtVNk",
            # "Cookie": f"locale=ru; __bsa=basket-ru-23; _ym_uid=167333934632215979; _ga=GA1.2.678603094.1688646291; _ga_EVJH2CFDRY=GS1.1.1688646291.1.0.1688646293.0.0.0; external-locale=ru; _ym_d=1693486717; enabled_feature_version=2; _wbauid=7809370961701797193; BasketUID=516f163bb2ca41c0a943bb11d234fd37; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UrQGgmYEdaKDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwZE3l0K08ODWQ/RWllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVgSFEZd2I/ezFWN0RzZys0EnMIHkofT0kwQn4rNH9mX19vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwdYUliJ0NcTwonHg1pN2wXPHVlLwkxLGJ5MVIvE0tsGA==AHvJaQ==; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UrQGgmYEdaKDVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwZE3l0K08ODWQ/RWllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVgSFEZd2I/ezFWN0RzZys0EnMIHkofT0kwQn4rNH9mX19vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwdYUliJ0NcTwonHg1pN2wXPHVlLwkxLGJ5MVIvE0tsGA==AHvJaQ==; x-supplier-id={META['suppliers'][supplier.name]['supplier_id']}; x-supplier-id-external={META['suppliers'][supplier.name]['supplier_id']}; ___wbu=ad213d68-eb6e-479e-923a-0aed27d24eaa.1704815201; WBToken=AqvfjQys6pHbDKy-pdwMU9GTkRGuIHk2A_GR-LnqPNsejuQCdzm6-eqOyFf5vB2zZ8ijReew-DoPF6_2VEBcdiQj1H3DIZk_VAeEXVt5g9ZNyFJwSAtgbdhPYkb8F3LRn6zI; cfidsw-wb=sd1Vlf86eK+sNQFcer61PQwfCh0/9i4R/sY39x3Lf5ghz+G7sLzJLRmtFOfeQ/Pq5tAisE4esT14bQ3Ga7HNUg6l8jEIE2vEc+ub4TAvZT/8YQc0PgSGEwm/HKZTt0G96fKeRiJew2pMt56RiKmhDEfd7AWOyp+YieWk+zle; cfidsw-wb=sd1Vlf86eK+sNQFcer61PQwfCh0/9i4R/sY39x3Lf5ghz+G7sLzJLRmtFOfeQ/Pq5tAisE4esT14bQ3Ga7HNUg6l8jEIE2vEc+ub4TAvZT/8YQc0PgSGEwm/HKZTt0G96fKeRiJew2pMt56RiKmhDEfd7AWOyp+YieWk+zle",
            

            "x-supplier-id": META['suppliers'][supplier.name]['supplier_id'],
            "x-supplier-id-external": META['suppliers'][supplier.name]['supplier_id'],
            "Content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            }
        self.headers.update(
            self.default_headers
        )
        
    def change_supplier(self, supplier: str) -> bool:
        pass
        # self.supplier = ClientSupplier(name=supplier)
        # self.headers.update({
        #         "Cookie": self.default_headers['Cookie']
        #         'x-supplier-id': self.supplier.id,
        #         'x-supplier-id-external': self.supplier.id
        # })
        # return self




class ClientSession(requests.Session):
    """This class is a prototype for all the fetchers, we implement them as a Sessions"""
    def __init__(self, supplier: ClientSupplier) -> None:
        requests.Session.__init__(self)
        self.supplier = supplier
        self.params: dict[str, str] = {}
        self.mount('https://', HTTPAdapter(max_retries=2))
        
    def construct_headers(self, is_stats: bool = False) -> None:
        """This method is for attaching headers to a session object depending on what data
        we are fetching, if it is for analytical data mostly - then `is_stats` argument is
        going to be set to True"""
        if is_stats:
            self.params.update(
                {
                    "key" : self.supplier.api_key
                }
            )
        self.headers.update(
                {
                    "Content-Type" : "application/json",
                    "accept" : "application/json",
                    "Authorization" : self.supplier.token
                }
            )

    def construct_jwt_headers(self, token_type: str = 'standard') -> None:
        """
        """
        self.headers.update(
                {
                    "Content-Type" : "application/json",
                    "accept" : "application/json",
                    "Authorization" : self.supplier.jwt_tokens[token_type]
                }
            )

    def prep_req(self, client_method) -> None:
        """Prepares request"""
        if client_method.api_engine == 'account':
            # self.construct_headers(is_stats=False)
            self.construct_jwt_headers(token_type='standard')
        elif client_method.api_engine == 'prices':
            self.construct_jwt_headers(token_type='prices')
        else:
            self.construct_jwt_headers(token_type='stats')
        

class ClientMethod:
    """Class for constructing methods a k a endpoints"""
    def __init__(
        self,
        api_method: Literal['GET', 'POST'], 
        api_endpoint: str,
        api_engine: str = 'stats'
    ) -> None:

        self.api_method = api_method
        self.api_endpoint = api_endpoint
        self.api_engine = api_engine
        if api_engine == 'account':
            self.url = BASE_URL + api_endpoint
        elif api_engine == 'back':
            self.url = BASE_SITE_URL + api_endpoint
        elif api_engine == 'prices':
            self.url = BASE_PRICE_URL + api_endpoint
        else:
            self.url = BASE_STATS_URL + api_endpoint
    

    # def prep_req(self, client_session: ClientSession) -> None:
    #     """Prepares request"""
    #     if self.api_engine == 'account':
    #         client_session.construct_headers(is_stats=False)
    #     else:
    #         client_session.construct_headers(is_stats=True)
    #     return client_session
        # if self.api_method == 'POST':
        #     client_session.post
