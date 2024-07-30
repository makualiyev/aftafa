from typing import Optional, List

from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel
from aftafa.client.megamarket.schemas.catalog_item import CatalogItem


class MerchantItemFeedUrl(BaseModel):
    URL: Optional[str]
    URL_id: Optional[int]
    password: Optional[str]
    path: Optional[str]
    port: Optional[str]
    url_type: Optional[str]
    user_name: Optional[str]

    class Config:
        alias_generator = to_camel


class MerchantItem(BaseModel):
    CC_stock_feed_host: Optional[str]
    CC_stock_feed_login: Optional[str]
    CC_stock_feed_pass: Optional[str]
    CC_stock_feed_path: Optional[str]
    CC_stock_feed_port: Optional[str]
    auto_cancel_orders: bool
    auto_confirm_orders: bool
    auto_confirmation_by_EAN: bool
    auto_confirmation_by_EAN_user_id: Optional[int]
    auto_rating: Optional[int]
    automatic_stock_size: Optional[int]
    confirmation_duration: Optional[int]
    confirmation_schedule_id: Optional[str]
    contract_id: Optional[str]
    date_create: Optional[str]
    date_update: Optional[str]
    email: Optional[str]
    feed_load_rate: Optional[int]
    feed_url: Optional[str]
    feed_urls: Optional[List[MerchantItemFeedUrl]]
    full_name: str
    hide_offers_order_daily_limit: Optional[int]
    integration_is_active: bool
    integration_order_cancel_url: Optional[str]
    integration_order_lable_update_url: Optional[str]
    integration_order_new_url: Optional[str]
    is_active: bool
    is_agreeing_to_the_terms_of_the_SBPG: bool
    is_blocked_by_merchant_cc: bool
    is_blocked_by_merchant_delivery: bool
    is_CC_order_section_enabled: bool
    is_change_date_of_shipment: bool
    is_DSM_order_section_enabled: bool
    is_delivery_order_section_enabled: bool
    is_feed_monitoring: bool
    is_mcs_section_enabled: bool
    is_notify_order_email: bool
    is_notify_order_SMS: bool
    is_personal_data_sending_available: bool
    is_print_name_on_marking_sheet: bool
    is_SBPG_lock: bool
    is_self_registration: bool
    is_services_section_available: bool
    is_shipment_part: bool
    is_sticker_tuning_enabled: bool
    is_unboxed_return: bool
    is_use_shipment_days_long: bool
    last_feed_date: Optional[str]
    max_shipment_days: Optional[int]
    merchant_id: int
    merchant_name: str
    orders_daily_limit: Optional[int]
    partner_id: str
    phone: Optional[str]
    static_rating: Optional[int]
    stock_source: Optional[str]
    stock_url: Optional[str]
    test_period_end_date: Optional[str]
    test_period_end_date_CC: Optional[str]
    test_period_end_date_DBM: Optional[str]
    time_zone: Optional[str]
    token: Optional[str]
    use_auto_rating: bool
    web_site_url: Optional[str]

    class Config:
        alias_generator = to_camel

class PostMerchantListResponseMeta(BaseModel):
    _source: str


class PostMerchantListResponseData(BaseModel):
    total: int
    totalNoFilter: int
    offset: int
    limit: int
    items: list[MerchantItem]


class PostMerchantListResponse(BaseModel):
    success: int
    meta: PostMerchantListResponseMeta
    data: PostMerchantListResponseData

    class Config:
        alias_generator = to_camel
