from urllib.parse import urljoin

from requests import PreparedRequest, Session, Response
from requests.auth import AuthBase


class BaseClient(Session):
    def __init__(self, baseurl: str = '') -> None:
        super().__init__()
        self.baseurl: str = baseurl

    def request(self, method, url, *args, **kwargs) -> Response:
        return super().request(
            method=method,
            url=urljoin(self.baseurl, url),
            *args,
            **kwargs
        )


class BaseAuth(AuthBase):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        return super().__call__(r)

# if __name__ == '__main__':
#     print(BaseClient())
