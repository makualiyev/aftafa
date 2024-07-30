from base64 import urlsafe_b64encode
import json
from requests import PreparedRequest, Response

from aftafa.client.baseclient import BaseClient, BaseAuth
from aftafa.common.config import Config


class ODataClientUser:
    def __init__(self, user: str) -> None:
        self.user = user
        self.meta = None
        self._get_meta_info()

    def _get_meta_info(self) -> None:
        cfg = Config()
        with open(cfg._get_meta_credentials_file(channel='OD'), 'rb') as f:
            meta_dump = json.load(f)
        self.meta = meta_dump.get('users').get(self.user)

    def _get_base64_str(self) -> str:
        con_str: str = ':'.join(
            [self.meta.get('account'), self.meta.get('password')]
        )
        con_b64_str = urlsafe_b64encode(con_str.encode()).decode()
        return con_b64_str

    @property
    def info(self) -> dict[str, str]:
        return {
            'account': self.meta.get('account'),
            'password': self.meta.get('password'),
            'basic_auth': self._get_base64_str()
        }


class ODataClientAuth(BaseAuth):
    """OData Authorization class."""
    def __init__(self, user: ODataClientUser) -> None:
        super().__init__()
        self.user = user

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers['Authorization'] = ('Basic ' + self.user.info['basic_auth'])
        return r
    

class ODataClient(BaseClient):
    """OData custom client"""
    def __init__(self, user: str, baseurl: str = '') -> None:
        super().__init__(baseurl)
        self.user = ODataClientUser(user=user)
        # self.headers.update({
        #     "Content-Type" : "application/json"
        # })

    def request(self, method, url, *args, **kwargs) -> Response:
        return super().request(
            method,
            url,
            *args,
            **kwargs,
            **{
                'auth': ODataClientAuth(user=self.user)
            }
        )
    
