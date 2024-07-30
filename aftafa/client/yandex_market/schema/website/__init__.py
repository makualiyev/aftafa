from typing import Optional
from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel


class DeliveryOptions(BaseModel):
        partner_type: Optional[str]
        day_from: str
        day_to: str
        price: float
        type: Optional[str]

        class Config:
            alias_generator = to_camel


class WebCatalogProductBenefit(BaseModel):
    type: str
    nested_types: list[Optional[str]]
    description: str
    is_primary: bool

    class Config:
        alias_generator = to_camel


class YandexBnplInfo(BaseModel):
    enabled: bool


class WebCatalogProductPromo(BaseModel):
    key: Optional[str]
    type: Optional[str]
    shop_promo_id: Optional[str]
    is_personal: bool

    class Config:
        alias_generator = to_camel


class WebCatalogProductAdditionalPrice(BaseModel):
    price_type: str
    price_value: float

    class Config:
        alias_generator = to_camel


class WebCatalogProductResultsPageParams(BaseModel):
    request_id: str
    page_number: int

    class Config:
        alias_generator = to_camel


class WebCatalogProductPromoAttributes(BaseModel):
    promo_key: str
    shop_promo_id: Optional[str]
    parent_promo_id: Optional[str]
    promo_type: str

    class Config:
            alias_generator = to_camel



class WebCatalogProduct(BaseModel):
    web_catalog_product_id: int = Field(alias='id')
    model_id: int
    sku_id: str
    offer_id: str
    market_sku_creator: str
    price: int
    old_price: int
    merch_price: Optional[int]
    vendor_id: int
    hid: int
    nid: int
    is_digital: bool
    offer_color: str
    product_id: int
    ware_id: str
    feed_id: int
    available_count: int
    shop_id: int
    supplier_id: int
    cashback_value: Optional[str]
    shop_sku: str = Field(alias='shop_sku')
    is_eda: bool
    is_express: bool
    warehouse_id: int
    is_any_express: bool
    is_bnpl: bool
    is_installments: bool
    business_id: int
    is_foodtech: int
    is_on_demand: bool
    ya_bank_price: str
    is_DSBS: bool
    has_resale_goods: bool
    pos: int
    req_id: Optional[str]
    variant: str
    brand_name: str
    has_address: int
    has_badge_new: bool
    has_badge_exclusive: bool
    has_badge_rare: bool
    viewtype: str
    offers_count: int
    min_price: str
    is_connected_retail: bool
    web_catalog_product_type: str = Field(alias='type')
    show_uid: str
    vat: str
    market_sku: str
    snippet_type: str = Field(alias='snippet_type')
    delivery_partner_types: list[Optional[str]]
    delivery_options: list[Optional[DeliveryOptions]]
    all_delivery_options: list[Optional[DeliveryOptions]]
    payment_types: list[Optional[str]]
    benefit: Optional[WebCatalogProductBenefit]
    yandex_bnpl_info: Optional[YandexBnplInfo]
    cashback_details_group_ids: list[Optional[str]]
    promos: list[Optional[WebCatalogProductPromo]]
    promo_attributes: list[Optional[WebCatalogProductPromoAttributes]] = Field(alias='promo_attributes')
    additional_prices: list[Optional[WebCatalogProductAdditionalPrice]]
    results_page_params: Optional[WebCatalogProductResultsPageParams]

    class Config:
        alias_generator = to_camel
