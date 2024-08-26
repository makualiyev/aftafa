from requests.models import Response


from aftafa.client.ozon.client import OzonSellerClient
from aftafa.common.source import HTTPDataSource
from aftafa.common.destination import JSONlDataDestination
from aftafa.client.ozon.schemas import PostDescriptionCategoryTreeResponse, v1GetTreeResponseItem


class OzonHTTPDataSource(HTTPDataSource):
    def __init__(self) -> None:
        self.domain = 'ozon'
        self.baseurl = 'api-seller.ozon.ru'

    def extract(self) -> None:
         return super().extract()


class CategoryResource(OzonHTTPDataSource):
    def __init__(self) -> None:
        self.name = 'POST /v1/description-category/tree'
        self.method = self.name.split(' ')[0]
        self.resource = self.name.split(' ')[1]

    def extract(self, http_client: OzonSellerClient | None = None) -> None:
        with client.request(
                    'POST',
                    '/v1/description-category/tree'
                ) as response:
                    if response.status_code == 200:
                        return response
                    

    def _validate_response(self, response: Response) -> bool:
        # try:
        #     schema_model: PostDescriptionCategoryTreeResponse = PostDescriptionCategoryTreeResponse(**response.json())
        #     return True
        # except ValidationError as e:
        #     print(f'ok')
        #     return False
        pass
    


if __name__ == '__main__':
      client = OzonSellerClient(supplier='dummy')
      category_resource = CategoryResource()
      r = category_resource.extract()
