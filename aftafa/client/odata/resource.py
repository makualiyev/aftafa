from requests.models import Response
from pydantic import ValidationError

from aftafa.client.odata.client import ODataClient
from aftafa.common.resource import HTTPResource
from aftafa.common.loader import XMLLoader


class ODataResource(HTTPResource):
    def __init__(self, name: str) -> None:
        self.name = name

    def extract(self, client: ODataClient) -> Response | None:
            with client.request(
                        'GET',
                        '/v1/description-category/tree'
                    ) as response:
                        if response.status_code == 200:
                            return response
                        else:
                            print('ok')

    def _check_response(self, response: Response) -> bool:
          content_type: str = response.headers['Content-Type'].split(';')[0]
          return content_type
    
    def _validate_response(self, response: Response) -> bool:
        # try:
        #     schema_model: PostDescriptionCategoryTreeResponse = PostDescriptionCategoryTreeResponse(**response.json())
        #     return True
        # except ValidationError as e:
        #     print(f'ok')
        #     return False
        pass
    
    def get_loader(self, data: Response, output_path: str) -> XMLLoader:
        loader = XMLLoader(data=data, output_path=output_path)
        return loader
    


if __name__ == '__main__':
      client = ODataClient(user='dummy')
    #   category_resource = CategoryResource()
    #   r = category_resource.extract()
