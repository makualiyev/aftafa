import json

from aftafa.common.config import Config


class OzonSellerSupplier:
    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.meta = None
        self._get_meta_info()

    def _get_meta_info(self) -> None:
        cfg = Config()
        with open(cfg._get_meta_credentials_file(channel='OZ'), 'rb') as f:
            meta_dump = json.load(f)
        self.meta = meta_dump.get('suppliers').get(self.supplier)

    @property
    def info(self) -> dict[str, str]:
        return {
            'client_id': self.meta.get('client_id'),
            'api_key': self.meta.get('api_key')
        }

    def _get_api_server(self, server: str) -> str:
        pass
