from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel
from aftafa.client.megamarket.schemas.order_search_item import OrderSearchItem


class PostOrderSearchResponseMeta(BaseModel):
    _source: str


class PostOrderSearchResponseData(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[OrderSearchItem]


class PostOrderSearchResponse(BaseModel):
    success: int
    meta: PostOrderSearchResponseMeta
    data: PostOrderSearchResponseData

    class Config:
        alias_generator = to_camel
