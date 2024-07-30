from requests.models import Response
from pydantic import ValidationError

from aftafa.client.baseclient import BaseClient
from aftafa.client.ozon.client import OzonSellerClient
from aftafa.common.resource import HTTPResource
from aftafa.common.loader import Loader
from aftafa.client.ozon.schemas import PostDescriptionCategoryTreeResponse, v1GetTreeResponseItem


class CategoryResource(HTTPResource):
    def __init__(self, name: str) -> None:
        self.name = name

    def extract(self, client: BaseClient) -> None:
            with client.request(
                        'POST',
                        '/v1/description-category/tree'
                    ) as response:
                        if response.status_code == 200:
                            return response

    def _validate_response(self, response: Response) -> bool:
        try:
            schema_model: PostDescriptionCategoryTreeResponse = PostDescriptionCategoryTreeResponse(**response.json())
            return True
        except ValidationError as e:
            print(f'ok')
            return False
    
    def get_loader(self) -> Loader:
        return super().get_loader()
    


if __name__ == '__main__':
      client = OzonSellerClient(supplier='dummy')
      category_resource = CategoryResource()
      r = category_resource.extract()
