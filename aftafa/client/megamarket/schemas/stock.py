from typing import Optional, List

from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel
from aftafa.client.megamarket.schemas.suggest_list_item import SuggestListItem


class PostStockGetResponseMeta(BaseModel):
    _requestId: str


class StockItemFact(BaseModel):
    quality: str
    quantity: int


class StockItem(BaseModel):
    facility_id: Optional[str]
    fact: List[StockItemFact]
    is_digital_mark_required: bool
    item_id: str
    item_image_link: Optional[str]
    item_name: Optional[str]
    item_url: Optional[str]
    value: int
    volume_weight: int

    class Config:
        alias_generator = to_camel

    def to_dict(self) -> dict:
        repr_ = self.dict()
        fact = repr_.get('fact')
        if not fact:
            repr_['fact_quality'] = 'GENERAL'
            repr_['fact_quantity'] = 0
            return [repr_]
        fact_storage = []
        for fact_ in fact:
            new_repr = self.dict()
            new_repr['fact_quality'] = fact_['quality']
            new_repr['fact_quantity'] = fact_['quantity']
            fact_storage.append(new_repr)
        return fact_storage


class PostStockGetResponseData(BaseModel):
    total: int
    items: List[Optional[StockItem]]


class PostStockGetResponse(BaseModel):
    success: int
    meta: PostStockGetResponseMeta
    data: PostStockGetResponseData

    class Config:
        alias_generator = to_camel
