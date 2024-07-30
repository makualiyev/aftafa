from typing import Optional, List

from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel


class PostCategoryListResponseDataCategoryItem(BaseModel):
    category_id: str
    structure_id: int
    parent_category_id: Optional[str]
    offer_count: Optional[int]
    name: str
    items: Optional[List['PostCategoryListResponseDataCategoryItem']]

    class Config:
        alias_generator = to_camel

    def to_dict(self) -> dict:
        def unnest_categories(d: dict, result=None) -> list[dict]:
            if result is None:
                result = []

            result.append({k: v for k, v in d.items() if k not in ('offer_count', 'items')})

            for item in d.get('items'):
                unnest_categories(item, result=result)

            return result
        
        return unnest_categories(self.dict())


class PostCategoryListResponseMeta(BaseModel):
    _source: str


class PostCategoryListResponse(BaseModel):
    success: int
    meta: PostCategoryListResponseMeta
    data: List[PostCategoryListResponseDataCategoryItem]

    class Config:
        alias_generator = to_camel
