import json
from typing import Optional, Union, Any
from pathlib import Path

import yaml
from pydantic.error_wrappers import ValidationError

from aftafa.utils.schema_resolver_model import OpenAPISpec


class OpenAPISchemaResolver:
    def __init__(
            self,
            path: str | Path
    ) -> None:
        if isinstance(path, str):
            path = Path(path)
        self.spec_file_path = path
        self._openapi_schema = self._init_openapi_schema()
        self._openapi_model = self._validate_openapi_schema()        
        self.paths = self._get_paths()

    def _init_openapi_schema(self) -> Optional[dict[str, Any]]:
        if self.spec_file_path.suffix == '.json':
            with open(self.spec_file_path, 'r', encoding='utf-8') as f:
                schema: dict[str, Any] = json.load(f)
        elif self.spec_file_path.suffix == '.yaml':
            with open(self.spec_file_path, 'rb') as f:
                schema: dict[str, Any] = yaml.load(f.read(), Loader=yaml.CLoader)
        else:
            raise TypeError(f"Error:no supported file format for -> {self.spec_file_path.suffix}")
        return schema
    
    def _validate_openapi_schema(self, schema: dict[str, Any] | None = None) -> OpenAPISpec | None:
        if not schema:
            schema = self._openapi_schema

        try:
            pyd_model: OpenAPISpec = OpenAPISpec(**schema)
        except ValidationError as valid_err:
            # If fields are missing just get rid of them
            fields_missing_condition: bool = (
                set([err['type'] for err in valid_err.errors()]) == set(["value_error.missing"])
                and
                set([err['loc'][0] for err in valid_err.errors()]) == set(["paths"])
            )
            if fields_missing_condition:
                print("This fields are missing:")
                for err_field in valid_err.errors():
                    print('\t', '->'.join(err_field['loc']))

                for err_field in set([err['loc'][1] for err in valid_err.errors()]):
                    schema["paths"].pop(err_field)

                pyd_model = OpenAPISpec(**schema)
            else:
                print(valid_err)
                return None
        return pyd_model

    def _get_paths(self) -> list[str]:
        return list(self._openapi_schema['paths'].keys())

    def get_response_content(self, path: str) -> None:
        methods: list[str] = list(self._openapi_schema['paths'][path].keys())
        return self._openapi_schema['paths'][path][methods[0]]['responses']['200']['content']
    
    def get_ref_from_schema(self, ref: str) -> None:
        return None
    
    def get_response_schema(self, path: str, method: str) -> None:
        schema_: dict[str, str] = self._openapi_schema['paths'][path][method.lower()]['response'][200]['content']['application/json']['schema']
        for key_, value_ in  schema_.items():
            if key_ == '$ref':
                pass

