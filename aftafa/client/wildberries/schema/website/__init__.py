from typing import Optional
from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel, to_lower


class V2CatalogDataProductSizePrice(BaseModel):
    basic: int
    product: int
    total: int
    logistics: int
    return_: int = Field(alias='return')


class V2CatalogDataProductSize(BaseModel):
    name: str
    orig_name: str
    rank: int
    option_id: int
    wh: int
    dtype: int
    price: V2CatalogDataProductSizePrice
    sale_conditions: int
    payload: Optional[str]

    class Config:
        alias_generator = to_camel


class V2CatalogDataProductColor(BaseModel):
    name: str
    id_: int = Field(alias='id')


class V2CatalogDataProduct(BaseModel):
    sort_: int = Field(alias='__sort')
    ksort: int
    time1: int
    time2: int
    wh: int
    dtype: int
    dist: int
    id_: int = Field(alis='id')
    root: int
    kind_id: int
    brand: str
    brand_id: int
    site_brand_id: int
    colors: list[Optional[V2CatalogDataProductColor]]
    subject_id: int
    subject_parent_id: int
    name: str
    supplier: str
    supplier_id: int
    supplier_rating: float
    supplier_flags: int
    pics: int
    rating: float
    review_rating: float
    feedbacks: int
    panel_promo_id: Optional[int]
    promo_text_card: Optional[str]
    promo_text_cat: Optional[str]
    volume: int
    view_flags: int
    sizes: list[Optional[V2CatalogDataProductSize]]
    total_quantity: int
    meta: Optional[dict]

    class Config:
        alias_generator = to_camel



class V2CatalogData(BaseModel):
    products: list[Optional[V2CatalogDataProduct]]
    total: int

    class Config:
        alias_generator = to_camel


class V2CatalogResponse(BaseModel):
    state: int
    version: int
    payload_version: int
    data: Optional[V2CatalogData]

    class Config:
        alias_generator = to_camel
