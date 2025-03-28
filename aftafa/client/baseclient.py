from urllib.parse import urljoin, quote

from requests import PreparedRequest, Session, Response
from requests.auth import AuthBase


class BaseUser:
    def __init__(self):
        pass

    
class BaseClient(Session):
    def __init__(self, name: str, baseurl: str = '') -> None:
        super().__init__()
        self.baseurl: str = baseurl
        self._client_name = name

    def request(self, method, url, *args, **kwargs) -> Response:
        return super().request(
            method=method,
            url=self.baseurl + quote(url),
            *args,
            **kwargs
        )


class BaseAuth(AuthBase):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        return super().__call__(r)
