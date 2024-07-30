from typing import Optional
from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel


class ItemGoodsAttributeGroup(BaseModel):
    title: str
    slug: str

    class Config:
        alias_generator = to_camel


class ItemGoodsAttribute(BaseModel):
    title: Optional[str]
    slug: Optional[str]
    value: Optional[str]
    group: Optional[ItemGoodsAttributeGroup]
    is_web_short: bool
    is_web_listing: bool
    sequence: int
    feature_description: Optional[str]

    class Config:
        alias_generator = to_camel


class ItemGoodsBox(BaseModel):
    box: str
    packaging_unit: str
    width: Optional[int]
    height: Optional[int]
    length: Optional[int]
    weight_unit: str
    weight: int

    class Config:
        alias_generator = to_camel


class ItemGoodsPackage(BaseModel):
    package_type: str
    min_quantity: str
    weight_unit: str

    class Config:
        alias_generator = to_camel


class ItemGoods(BaseModel):
    goods_id: str
    title: str
    title_image: str
    attributes: list[Optional[ItemGoodsAttribute]]
    web_url: str
    slug: str
    boxes: list[Optional[ItemGoodsBox]]
    category_id: Optional[str]
    brand: Optional[str]
    content_flags: list[Optional[str]]
    content_flags_str: list[Optional[str]]
    stocks: Optional[int]
    photos_count: Optional[int]
    offers_count: Optional[int]
    logistic_tags: list[Optional[str]]
    images: list[Optional[str]]
    documents: list[Optional[str]]
    description: Optional[str]
    videos: list[Optional[str]]
    main_collection_id: Optional[str]
    package: Optional[ItemGoodsPackage]
    
    
    class Config:
        alias_generator = to_camel


class ItemDeliveryPossibility(BaseModel):
    code: str
    date: str
    amount: int
    is_default: bool
    max_delivery_days: Optional[int]
    applied_promotion_tags: list[Optional[str]]
    is_dbm: bool
    delivery_price_type: Optional[str]
    display_name: Optional[str]
    display_delivery_date: Optional[str]
    delivery_options: list[Optional[str]]

    class Config:
        alias_generator = to_camel

        
class ItemFavoriteOffer(BaseModel):
    favorite_offer_id: str = Field(alias='id')
    price: int
    score: float
    is_favorite: bool
    merchant_id: str
    delivery_possibilities: list[Optional[ItemDeliveryPossibility]]
    final_price: Optional[int]
    bonus_percent: Optional[int]
    bonus_amount: Optional[int]
    available_quantity: Optional[int]
    bonus_amount_final_price: Optional[int]
    discounts: list[Optional[str]]
    price_adjustments: list[Optional[str]]
    delivery_date: Optional[str]
    pickup_date: Optional[str]
    merchant_offer_id: Optional[str]
    merchant_name: str
    merchant_logo_url: str
    merchant_url: str
    merchant_summary_rating: Optional[float]
    is_bpg_by_merchant: bool
    nds: Optional[float]
    old_price: Optional[float]
    old_price_change_percentage: Optional[float]
    max_delivery_days: Optional[str]
    bpg_type: str
    credit_payment_amount: Optional[int]
    installment_payment_amount: Optional[float]
    show_merchant: Optional[str]
    sales_block_info: Optional[str]
    due_date: Optional[str]
    due_date_text: Optional[str]
    location_id: Optional[str]
    spasibo_is_available: bool
    is_showcase: bool
    loyalty_promotion_flags: list[Optional[str]]
    prices_per_measurement: list[Optional[str]]
    available_payment_methods: list[Optional[str]]
    super_price: Optional[float]
    warehouse_id: Optional[str]
    bnpl_payment_params: Optional[str]
    installment_payment_params: Optional[str]
    bonus_info_groups: list[Optional[str]]
    calculated_delivery_date: Optional[str]

    
    class Config:
        alias_generator = to_camel


class ItemRanking(BaseModel):
    value: Optional[str]
    value_bi: Optional[str]

    class Config:
        alias_generator = to_camel


class ItemAuctionInfoAnalytics(BaseModel):
    ad_code: Optional[str]
    ad_name: Optional[str]
    campaign_code: Optional[str]
    campaign_name: Optional[str]
    advertiser_id: Optional[int]
    advertiser_name: Optional[str]
    channels: list[Optional[str]]
    place_name: list[Optional[str]]
    amaz_me_reference: Optional[str]
    ad_mark: Optional[str]
    campaign_type: Optional[str]

    class Config:
        alias_generator = to_camel


class ItemAuctionInfoOrd(BaseModel):
    show_badge: bool
    organization_name: Optional[str]
    creative_marker: Optional[str]

    class Config:
        alias_generator = to_camel


class ItemAuctionInfo(BaseModel):
    analytics: ItemAuctionInfoAnalytics
    auction_info_ord: ItemAuctionInfoOrd = Field(alias='ord')


    class Config:
        alias_generator = to_camel



class Item(BaseModel):
    goods: ItemGoods
    price: int
    price_from: Optional[int]
    price_to: Optional[int]
    bonus_percent: Optional[int]
    bonus_amount: Optional[int]
    rating: Optional[float]
    review_count: Optional[int]
    offer_count: Optional[int]
    final_price: Optional[int]
    favorite_offer: ItemFavoriteOffer
    related_items: list[Optional[str]]
    product_selectors: list[Optional[str]]
    extra_options: list[Optional[str]]
    delivery_possibilities: list[Optional[ItemDeliveryPossibility]]
    discounts: list[Optional[str]]
    content_flags_str: list[Optional[str]]
    content_flags: list[Optional[str]]
    badges: list[Optional[str]]
    crossed_price: Optional[float]
    crossed_price_period: Optional[str]
    last_price: Optional[int]
    is_available: bool
    crossed_price_change_percentage: Optional[float]
    collections: list[Optional[str]]
    has_other_offers: bool
    ranking: ItemRanking
    auction_info: ItemAuctionInfo

    class Config:
        alias_generator = to_camel


class Sorting(BaseModel):
    name: Optional[str]
    value: Optional[int]

    class Config:
        alias_generator = to_camel


class Navigation(BaseModel):
    selected_node: Optional[str]
    child_nodes: list[Optional[str]]
    parent_nodes: list[Optional[str]]

    class Config:
        alias_generator = to_camel


class Processor(BaseModel):
    type: Optional[str]
    goods_id: Optional[str]
    collection_id: Optional[str]
    menu_node_id: Optional[str]
    merchant_id: Optional[str]
    merchant_slug: Optional[str]
    url: Optional[str]
    brand_slug: Optional[str]
    merchant_logo_url: Optional[str]
    menuNode_title: Optional[str]
    selected_filters: list[Optional[str]]

    class Config:
        alias_generator = to_camel


class Collection(BaseModel):
    collection_id: Optional[str] = Field(alias='id')
    name: Optional[str]
    slug: Optional[str]
    web_url: Optional[str]
    is_selected: bool
    child_collections: list[Optional['Collection']]
    is_active: bool
    relative_url: Optional[str]
    type: Optional[str]
    image_url: Optional[str]

    class Config:
        alias_generator = to_camel


class CollectionSelector(BaseModel):
    collections: list[Optional[Collection]]

    class Config:
        alias_generator = to_camel


class CategoryImage(BaseModel):
    mid10: str

    class Config:
        alias_generator = to_camel


class Category(BaseModel):
    collection_id: str
    parent_id: str
    collection_type: str
    title: str
    is_department: bool
    hierarchy: list[Optional[str]]
    url: str
    images: Optional[CategoryImage]
    description: str
    slug: str
    navigation_mode: str
    allowed_service_schemes: list[Optional[str]]
    code: str
    main_listing_collection_id: str
    attributes: Optional[str]
    rating: Optional[dict[str, str]]
    short_title: str
    main_listing_collection_relative_url: str
    name: str
    display_name: str

    class Config:
        alias_generator = to_camel


class Meta(BaseModel):
    time: str
    trace_id: str
    request_id: str
    app_version: str

    class Config:
        alias_generator = to_camel


class CatalogSearchResponse(BaseModel):
    success: bool
    meta: Meta
    errors: list[Optional[str]]
    total: Optional[str]
    offset: Optional[str]
    limit: Optional[str]
    items: list[Optional[Item]]
    tags: list[Optional[str]]
    categories: list[Category]
    merchant_ids: list[Optional[str]]
    price_range: Optional[str]
    filters: list[Optional[str]]
    selected_filter_count: Optional[int]
    collection_selector: Optional[CollectionSelector]
    processor: Optional[Processor]
    has_plus_18: bool
    navigation: Optional[Navigation]
    flags: list[Optional[str]]
    keywords: list[Optional[str]]
    view: Optional[str]
    allowed_service_schemes: list[Optional[str]]
    sorting: list[Optional[Sorting]]
    listing_size: Optional[int]
    assumed_collection: Optional[str]
    alternative_assumed_collections: list[Optional[str]]
    query_changes_info: Optional[str]
    search_text_context: Optional[str]
    goods_url: Optional[str] = Field(alias='goodsURL')
    version: Optional[str]

    class Config:
        alias_generator = to_camel
