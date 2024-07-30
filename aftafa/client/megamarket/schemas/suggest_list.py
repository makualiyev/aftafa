from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel
from aftafa.client.megamarket.schemas.suggest_list_item import SuggestListItem


class PostSuggestListResponseMeta(BaseModel):
    _source: str


class PostSuggestListResponseData(BaseModel):
    total: int
    items: list[SuggestListItem]


class PostSuggestListResponse(BaseModel):
    success: int
    meta: PostSuggestListResponseMeta
    data: PostSuggestListResponseData

    class Config:
        alias_generator = to_camel
