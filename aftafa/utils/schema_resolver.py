"""
Schema resolver for OpenAPI/Swagger documented APIs.
"""

import typing as tp

import yaml


class SwaggerSchemaResolver:
    def __init__(
            self,
            client: str = 'wildberries'
    ) -> None:
        self.client = client
        with open(f'sennix/client/{self.client}/docs/swagger.yaml', 'rb') as f:
            swagger_yaml = yaml.load(f.read(), Loader=yaml.CLoader)
        self.swagger_yaml = swagger_yaml
        self.paths = self._get_paths()

    def get_meta(self) -> None:
        pass

    def _get_paths(self) -> list[str]:
        return list(self.swagger_yaml['paths'].keys())

    def get_response_content(self, path: str) -> None:
        return self.swagger_yaml['paths'][path]['get']['responses'][200]['content']
    
    def get_ref_from_schema(self, ref: str) -> None:
        path_to: list[str] = [ref_part for ref_part in ref.split('/') if ref_part != '#']
        for path_to_part in path_to:
            self.swagger_yaml.get(path_to_part)
    
    def get_response_schema(self, path: str) -> None:
        schema_: dict[str, str] = self.swagger_yaml['paths'][path]['get']['response'][200]['content']['application/json']['schema']
        for key_, value_ in  schema_.items():
            if key_ == '$ref':
                pass
