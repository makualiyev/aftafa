import os
import json

from requests import Session

from aftafa.common.config import Config


cfg: Config = Config()
META = cfg._get_meta_credentials_file('MV')

BASE_URL = 'https://sellers.mvideoeldorado.ru'

class ApiClient:
    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.tokens: dict[str, str] = {}
        self.headers = {
            "Accept" : "application/json, text/plain, */*",
            "Content-Type" : "application/json",
            "Connection": "keep-alive",
            "Origin": BASE_URL,
            "Referer" : BASE_URL + "/login/authorization",
            "sec-ch-ua" : '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            "sec-ch-ua-mobile" : "?0",
            "sec-ch-ua-platform" : '"Windows"',
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
        }
        self.payload = {
            "password": META['users'][self.supplier]['password'],
            "username":META['users'][self.supplier]['login'],
            "clientName":"mpa-web",
            "grantType":"password"
        }


    def authorize(self) -> Session:
        sesh = Session()
        sesh.headers.update(self.headers)
        with sesh.post(
                    url=(BASE_URL + '/api/v1/auth/realms/master/openid-connect/token'),
                    json=self.payload,
                    verify=False
                ) as response:
            if response.status_code == 200:
                self.tokens['token'] = response.json()['accessToken']
                self.tokens['refresh_token'] = response.json()['refreshToken']
        sesh.headers.update({
            "Accept" : "application/mvideo.api.v1+json",
            "Content-Type" : "application/mvideo.api.v1+json",
            "Authorization" : f"Bearer {self.tokens['token']}"
        })
        sesh.supplier = {
            'code': META['users'][self.supplier]['code']
        }
        return sesh
    
    def _preauthorize(self, sms_code: str) -> int:
        """new method (using SMS code verification)"""
        sesh = Session()
        sesh.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru',
            'baggage': 'sentry-environment=prod,sentry-release=67.4.0,sentry-public_key=32ab3faef5f4a31f9d0b5f05d749ec45,sentry-trace_id=423d48d1b18843639a18ec93f0f577b6',
            'content-type': 'application/json',
            # 'cookie': '_ym_uid=1648723353491300865; session-id=6fb53c50-ca94-45a3-b93e-b276eea7ff86; _ym_d=1712563028; _ym_isad=2; JSESSIONID=15B5A544DBC600A765C214AF66BC7AE6; _ym_visorc=w',
            'ngsw-bypass': 'true',
            'origin': 'https://sellers.mvideoeldorado.ru',
            'priority': 'u=1, i',
            'referer': 'https://sellers.mvideoeldorado.ru/login/authorization',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sentry-trace': '423d48d1b18843639a18ec93f0f577b6-ac664bb0ba38468f',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        })
        json_data = {
            'username': META['users'][self.supplier]['login'],
            'password': META['users'][self.supplier]['password'],
        }

        with sesh.post(
                    url=(BASE_URL + '/api/auth-proxy/authenticate/password'),
                    json=json_data
                ) as response:
            if response.status_code == 200:
                verification_id = response.json()['verificationId']
        # response will be -> {verificationId: 446007894, timeLeftUntilNextAttempt: 59, attempt: 1, phone: "+79686845991"}
        json_data = {
                'phone': '+79685843981',
                'code': sms_code,
                'verificationId': verification_id,
            }
        with sesh.post(
                    url=(BASE_URL + '/api/auth-proxy/verification'),
                    json=json_data
                ) as response:
            if response.status_code == 200:
                self.tokens['token'] = response.json()['accessToken']
                self.tokens['refresh_token'] = response.json()['refreshToken']

        sesh.headers.update({
            "Accept" : "application/mvideo.api.v1+json",
            "Content-Type" : "application/mvideo.api.v1+json",
            "Authorization" : f"Bearer {self.tokens['token']}"
        })
        sesh.supplier = {
            'code': META['users'][self.supplier]['code']
        }
        return sesh
        # response will be
        #{
        #  "accessToken": "eyJ0eXAiOiJKV1QiLCJraWQiOiJjZnV5VEJtQUNjYWt6T3YyMnJxcHFrUzBVT2ZmWHdiTEt4emFsTktTZlRVIiwiYWxnIjoiUlMyNTYifQ.eyJqdGkiOiIxMmMxMzZjYS03MWE3LTRlYzItYmM2Yy04Zjk5NzExYjNiNDIiLCJpYXQiOjE3MjA2OTI5NzMsImlzcyI6Ii9hcGkvdjEvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXpwIjoibXBhLWJmZiIsInN1YiI6Im1ha3UuYWxpeWV2QHlhbmRleC5ydSIsInNlc3Npb25fc3RhdGUiOiI2OGI4NjE4Ni04OTg3LTRjYTEtODIwYi01Y2E4MjdjMmI5N2QiLCJhdWQiOlsibXBhLWJmZiIsIm1wYS1iYWNrLWNvcmUiXSwidHlwIjoiYmVhcmVyIiwiZW1haWwiOiJtYWt1LmFsaXlldkB5YW5kZXgucnUiLCJwaG9uZV9udW1iZXIiOiI5Njg1ODQzOTgxIiwicHJlZmVycmVkX3VzZXJuYW1lIjoi0JDQu9C40LXQsiDQnNCw0LPRgdGD0LQgIiwiZXhwIjoxNzIwNzc5MzczLCJtcGFfdWlkIjoiNzI2ODVkMDYtMTU5Yi00YjBjLTliZjItODg1NWI0ZDIzODE5Iiwic3VwcGxpZXJDb2RlIjoiSzAwMDA1NDI2MSIsInJlc291cmNlX2FjY2VzcyI6eyJtcGEtYmZmIjpbeyJyb2xlIjoibXBhX3N0b2NrcyIsInBlcm1pc3Npb25zIjpbIk1QQV9FRElUX1NUT0NLUyIsIk1QQV9SRUFEX1NUT0NLUyJdfSx7InJvbGUiOiJNUEFfQ0xJRU5UX1JFUE9SVF9SRUFERVJfQkFTSUMiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVQT1JUX0NMSUVOVFNfQkFTSUMiXX0seyJyb2xlIjoiTVBBX0NMSUVOVF9SRVBPUlRfUkVBREVSIiwicGVybWlzc2lvbnMiOlsiTVBBX1JFUE9SVFNfQ0xJRU5UUyJdfSx7InJvbGUiOiJtcGFfbWFya2V0cGxhY2VfcHJvZHVjdF9yZWFkZXIiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVBRF9QUk9EVUNUU19NQVJLRVRQTEFDRSJdfSx7InJvbGUiOiJNUEFfT01fU1VQUExJRVIiLCJwZXJtaXNzaW9ucyI6WyJvbV9mYm1fc2V0dGluZ3Nfd2FyZWhvdXNlX3N1cHBseV9lZGl0Iiwib21fZmJtX2Zvcm1fYXBwbGljYXRpb25fcmVwb3J0X3JlYWQiLCJvbV9vcmRlcl9yZXBvcnQiLCJvbV9mYm1fc2V0dGluZ3Nfd2FyZWhvdXNlX3N1cHBseV9zdXBwbGllciIsIm9tX2ZibV9zZWN0aW9uX29yZGVyc2ZibV9yZWFkX3NlcnZpY2VzX3N1cHBsaWVyIiwib21fZmJtX2Zvcm1fYXBwbGljYXRpb25fZGVsZXRlIiwib21fZmJtX2Zvcm1fYXBwbGljYXRpb25fY3JlYXRlIiwib21fZmJtX3NlY3Rpb25fb3JkZXJzZmJtX3JlcG9ydF9yZWFkIiwib21fb3JkZXJfcmVhZF9zdXBwbGllciIsIm9tX2ZibV9zZWN0aW9uX3NldHRpbmdfbGltaXRzX3JlYWRfc2VydmljZXNfc3VwcGxpZXIiLCJvbV9mYm1fc2VjdGlvbl9mb3JtYXBwbGljYXRpb25fcmVhZF9zZXJ2aWNlcyIsIm9tX2ZibV9yZWFkX3NlcnZpY2VzX3N1cHBsaWVyIiwib21fZmJtX2Zvcm1fYXBwbGljYXRpb25fZWRpdCJdfSx7InJvbGUiOiJtcGFfcGFydG5lcl9tYXJrZXRwbGFjZSIsInBlcm1pc3Npb25zIjpbIk1QQV9SRUFEX1JFVEFJTF9QUklDRVMiLCJNUEFfRURJVF9RVU9UQVMiLCJNUEFfRURJVF9PUkRFUlMiLCJiaWxsaW5nX3JlYWRfc3VwcGxpZXJfcmVwb3J0IiwiTVBBX1JFQURfT1JERVJTIiwiTVBBX0VESVRfUkVUQUlMX1BSSUNFUyIsIk1QQV9SRUFEX1BNUkVQT1JUUyIsIk1QQV9SRUFEX1BST01PIiwiTVBBX1JFQURfUVVPVEFTIl19LHsicm9sZSI6Im1wYV9tYXJrZXRwbGFjZV9wcm9kdWN0X2Z1bGwiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVBRF9QUk9EVUNUU19NQVJLRVRQTEFDRSIsIk1QQV9FRElUX1BST0RVQ1RTX01BUktFVFBMQUNFIl19LHsicm9sZSI6Im1wYV9wYXJ0bmVyX3NhbGVzX3JlcG9ydCIsInBlcm1pc3Npb25zIjpbIk1QQV9SRUFEX1NBTEVTX1JFUE9SVCJdfSx7InJvbGUiOiJtcGFfcGFydG5lcl9zYWxlc19kYXNoYm9hcmQiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVBRF9TQUxFU19EQVNIQk9BUkQiXX0seyJyb2xlIjoibXBhX3BhcnRuZXJfcHJvbW9fM3AiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVBRF9QUk9NT18zUCJdfSx7InJvbGUiOiJCSUxMSU5HX1NVUFBMSUVSIiwicGVybWlzc2lvbnMiOlsiYmlsbGluZ19zdXBwbGllcl9yZXBvcnRfcmVhZCIsImJpbGxpbmdfcmVhZF9zZXJ2aWNlcyJdfSx7InJvbGUiOiJNUEFfUlREX1JFUE9SVF9SRUFERVJfQkFTSUMiLCJwZXJtaXNzaW9ucyI6WyJNUEFfUkVQT1JUX1JURF9CQVNJQyJdfSx7InJvbGUiOiJtcGFfdmFsaWRhdGVkIiwicGVybWlzc2lvbnMiOlsiTVBBX0NIQU5HRV9QQVNTV09SRCIsIk1QQV9SRUFEX0ZCTUVTU0FHRVMiLCJNUEFfUkVTRVRfUEFTU1dPUkQiLCJNUEFfRURJVF9VU0VSIiwiTVBBX1JFQURfQU5OT1VOQ0VNRU5UIiwiTVBBX0NIQU5HRV9FTUFJTCIsIk1QQV9FRElUX0NPTVBBTlkiLCJNUEFfUkVBRF9DT01QQU5ZIl19LHsicm9sZSI6Im1wYV9hcGlfa2V5IiwicGVybWlzc2lvbnMiOlsiTVBBX1JFQURfQVBJX0tFWSIsIk1QQV9FRElUX0FQSV9LRVkiLCJNUEFfUkVNT1ZFX0FQSV9LRVkiXX1dLCJtcGEtYmFjay1jb3JlIjpbeyJyb2xlIjoibXBhX3N0b2NrcyIsInBlcm1pc3Npb25zIjpbIk1QQV9FRElUX1NUT0NLUyIsIk1QQV9SRUFEX1NUT0NLUyJdfSx7InJvbGUiOiJtcGFfcGFydG5lcl9tYXJrZXRwbGFjZSIsInBlcm1pc3Npb25zIjpbIk1QQV9SRUFEX1JFVEFJTF9QUklDRVMiLCJNUEFfUkVBRF9QUk9EVUNUU19NQVJLRVRQTEFDRSIsIk1QQV9FRElUX1FVT1RBUyIsIk1QQV9FRElUX09SREVSUyIsImJpbGxpbmdfcmVhZF9zdXBwbGllcl9yZXBvcnQiLCJNUEFfUkVBRF9PUkRFUlMiLCJNUEFfRURJVF9SRVRBSUxfUFJJQ0VTIiwiTVBBX0VESVRfUFJPRFVDVFNfTUFSS0VUUExBQ0UiLCJNUEFfUkVBRF9RVU9UQVMiXX1dfX0.AWKHrM2Wp0IUeqCG6KxSiBwDmRF3s1MZBADPDkn7NY0MaH_jKMGB0KWYoXq3lCCfXLJk722gr4rT6qaG143z2j6YIj5MgRMQxTThw2OgH1u3NDLSywwOBoF6hERQztcC5Slux1TQH5pcOTr-Rw7L6kdQF-adVebf3mFpN1Q3oiZz947aya7zqwZCJpMoRbHRvtBTXSQo7IG7yw0uGYhEq5b18m5D_qHdFWKEMcjyUabJgd4Cw19wY1pOPwJRU5XDvTfVYsOH4iXt1N-QtAssSj3QL8FClA79FXZCNITw2LDLg7f-qJ-_OOnK1aIf5AvqvOHTCASAODgKoL0_VwbTVA",
        #  "expiresAt": 1720779373,
        #  "expiresIn": 86400,
        #  "refreshExpiresAt": 1720779373,
        #  "refreshExpiresIn": 86400,
        #  "refreshToken": "eyJ0eXAiOiJKV1QiLCJraWQiOiJjZnV5VEJtQUNjYWt6T3YyMnJxcHFrUzBVT2ZmWHdiTEt4emFsTktTZlRVIiwiYWxnIjoiUlMyNTYifQ.eyJqdGkiOiJkZjY1MWE2NC1kMTg2LTQ0OTgtYjYxYS1iYWViMjlhYmJjZDEiLCJpYXQiOjE3MjA2OTI5NzMsImlzcyI6Ii9hcGkvdjEvYXV0aC9yZWFsbXMvbWFzdGVyIiwiYXpwIjoibXBhLWJmZiIsInN1YiI6Im1ha3UuYWxpeWV2QHlhbmRleC5ydSIsInNlc3Npb25fc3RhdGUiOiI2OGI4NjE4Ni04OTg3LTRjYTEtODIwYi01Y2E4MjdjMmI5N2QiLCJhdWQiOlsibXBhLWJmZiIsIm1wYS1iYWNrLWNvcmUiXSwidHlwIjoicmVmcmVzaCIsImVtYWlsIjoibWFrdS5hbGl5ZXZAeWFuZGV4LnJ1IiwicGhvbmVfbnVtYmVyIjoiOTY4NTg0Mzk4MSIsInByZWZlcnJlZF91c2VybmFtZSI6ItCQ0LvQuNC10LIg0JzQsNCz0YHRg9C0ICIsImV4cCI6MTcyMDc3OTM3M30.kUtnrvrTgVIvcKVzXoeLO4A2RC4hGHengtHa6mIs509l8tMuYWYj0P9L6OclNNeS4ZR-cL8PHWXlXeUYzucV61RjJjPF_yeLhXStp20vfGVcxoKADUWoAfA19xYhRxAsC5sNMN-DFDdWI64xGb7mA4ZKJU673vBMQ89eZem6dheaAuPkIp4NvRZY6sbaHfvXU26HV3FcyTxwN7shteHRQ3PR71XgTsFfFfNBsfRJ58SXt6kJsRsiuJl2WhMOv4TH8ZveFb4xQyncCMtdIrkRSgR0f1VCBxGkMLluGoHy1KWdjrCgxPo0AJQGf60MRZOEuFvr5EGdGC-eyO17KMk2-g"
        # }




class MPmethod(object):
    def __init__(self, api_method : str, api_endpoint : str, api_engine : str = 'apiseller') -> None:
        self.api_method = api_method
        self.api_endpoint = api_endpoint
        self.url = BASE_URL + api_endpoint