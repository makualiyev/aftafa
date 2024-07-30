import json


class WildberriesSupplier:
    def __init__(self, supplier: str) -> None:
        self.supplier = supplier
        self.meta = None
        self._get_meta_info()

    def _get_meta_info(self) -> None:
        with open('sennetl/env/wildberries.json', 'rb') as f:
            meta_dump = json.load(f)
        self.meta = meta_dump.get('suppliers').get(self.supplier)

    @property
    def info(self) -> dict[str, str]:
        return {
            'jwt_token__stats': self.meta.get('jwt_tokens').get('stats')
        }
    
    def _get_api_server(self, server: str) -> str:
        pass
    