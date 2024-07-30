from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel
from aftafa.client.megamarket.schemas.catalog_item import CatalogItem


class PostCatalogGetListResponseMeta(BaseModel):
    _source: str


class PostCatalogGetListResponseData(BaseModel):
    total: int
    items: list[CatalogItem]


class PostCatalogGetListResponse(BaseModel):
    success: int
    meta: PostCatalogGetListResponseMeta
    data: PostCatalogGetListResponseData

    class Config:
        alias_generator = to_camel
