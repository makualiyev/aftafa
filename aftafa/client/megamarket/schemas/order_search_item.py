from __future__ import annotations
from typing import List, Dict, Union, Optional, Literal
from enum import Enum

from pydantic import BaseModel, Field, constr, Extra

import aftafa.client.megamarket.models as sbermm_models
from aftafa.utils.helpers import to_camel


MerchantIdNumbers = constr(regex=r'^[0-9]+$')

class OrderStatusEnum(str, Enum):
    DELIVERED = "DELIVERED"
    CUSTOMER_CANCELED = "CUSTOMER_CANCELED"
    PACKED = "PACKED"
    MERCHANT_CANCELED = "MERCHANT_CANCELED"
    CONFIRMED = "CONFIRMED"
    SHIPPING_EXPIRED = "SHIPPING_EXPIRED"
    NEW = "NEW"
    SHIPPED= "SHIPPED"
    

class OrderSubStatusEnum(str, Enum):
    LATE_REJECT = "LATE_REJECT"
    CONFIRMATION_EXPIRED = "CONFIRMATION_EXPIRED"
    
    
class OrderSearchItemItemsGoodsData(BaseModel):
    name: str
    is_digital_mark_required: bool
    
    class Config:
        alias_generator = to_camel
        
        
class OffersV2Item(BaseModel):
    merchant_id: int = Field(..., alias='merchantId')
    region: Optional[List[int]]
    price: int
    type: str
    service_scheme: str
    favorite_price_for_regions: Optional[List[int]]
    favorite: bool
    group: int
    old_price: Optional[int]
    
    
class GoodsCardCategory(BaseModel):
    master: List[List[str]]
    web: List[List[str]]
    sandbox: Optional[List[List[str]]]
    
    
class GoodsCardAttributes(BaseModel):
    name: str
    group: str
    sequence: int
    purpose: Optional[List[str]]
    units: str
    type: str
    feature_description: str
    value: List[str]
    
    
class GoodsCardImage(BaseModel):
    image_link: str
    image_order: str


class GoodsCardDocument(BaseModel):
    document_link: str


class GoodsCardExtra(BaseModel):
    attributes_on_page: int
    is_attributes_over_page: int
    
    
class DeputySelector(BaseModel):
    name: Optional[str]
    control_type: Optional[str]
    value: Optional[str]


class GoodsCardDeputy(BaseModel):
    rule_id: Optional[str]
    deputy_id: Optional[str]
    fraction_id: Optional[str]
    selector_plp: Optional[Union[DeputySelector, list[DeputySelector]]]
    selector_pdp: Optional[Union[DeputySelector, list[DeputySelector]]]
    
    
class GoodsCardNestedRatingItem(BaseModel):
    collection_id: str
    value: int
    value_bi: Optional[int]
    
    
class GoodsCardNestedFilter(BaseModel):
    id: str
    string_values: Optional[List[str]]
    float_values: Optional[List[int]]
    
    
class GoodsCardBox(BaseModel):
    box: str
    packaging_unit: str
    width: int
    height: int
    length: int
    weight_unit: str
    weight: int
    
    
class PriceHistoryItem(BaseModel):
    point_id: int
    point_name: str
    point_value: int


class PriceAdjustment(BaseModel):
    type: str
    amount: int


class FavoriteOffer(BaseModel):
    offer_id: Optional[str]
    price: Optional[int]
    partner_id: Optional[str]
    contract_id: Optional[str]
    merchant_id: Optional[str]
    merchant_name: Optional[str]
    old_price: Optional[int]


class Offer(BaseModel):
    merchant_id: int
    price: int
    type: str
    merchant_name: str
    regions_1: int
    regions_2: int


class MerchantBonusField(BaseModel):
    k: int
    merchant_id: str
    merchant_name: str
    bonus_date: str


class MerchantBonus(BaseModel):
    __root__: Dict[MerchantIdNumbers, MerchantBonusField]

    def __iter__(self):
        return iter(self.__root__)
    
    def __getitem__(self, item):
        return self.__root__[item]


class Bonus(BaseModel):
    k: int
    bonus_date: str
    merchant_bonus: MerchantBonus
    
    
class GoodsCardPriceExtra(BaseModel):
    bpg2_competitors: Optional[int]


class GoodsCardPrice(BaseModel):
    is_available: int
    price_date: str
    last_price: Optional[int]
    final_price: Optional[int]
    crossed_price: Optional[int]
    crossed_price_term: Optional[str]
    min_price: Optional[int]
    max_price: Optional[int]
    total_offers: int
    discounts: List
    favorite_offer: FavoriteOffer
    offers: List[Offer]
    bonus: Bonus
    extra: Optional[GoodsCardPriceExtra]
    price_history: List[PriceHistoryItem]
    delivery_date: str
    price_change_percentage: Optional[float]
    price_adjustments: List[PriceAdjustment]
    

class OrderSearchItemItemsGoodsCard(BaseModel):
    rate: Optional[int]
    min_fee: Optional[str]
    item_id: str
    purpose: List[str]
    display_on_web: int
    single_offer_card: bool
    long_web_name: str
    short_web_name: str
    prices: GoodsCardPrice
    offers_v2: Optional[List[OffersV2Item]]
    brand: str
    brand_slug: str
    badges: Optional[List[str]]
    category: Optional[GoodsCardCategory]
    country_of_origin: Optional[str]
    gtins: List[str]
    logistic_class: str
    logistic_class_code: int
    logistic_class_type: int
    long_description: str
    manufacturer_part_no: str
    model: str
    multiboxes_possible: str
    nds: str
    operation: str
    original_barcode: Optional[str]
    popularity: int
    registry_name: str
    series: Optional[str]
    short_description: str
    slug: str
    sub_brand: str
    toplist: int
    warranty: str
    warranty_type: str
    attributes: List[GoodsCardAttributes]
    video: str
    images: List[GoodsCardImage]
    thumbnail: str
    documents: Optional[List[GoodsCardDocument]]
    boxes: Optional[List[GoodsCardBox]]
    flags: Optional[List[str]]
    collections: List[int]
    main_web_collection_id: int
    update_at: str
    url: str
    reviews_count: int
    reviews_rating: int
    reviews_show: int
    extra: GoodsCardExtra
    successor: Optional[str]
    deputy: GoodsCardDeputy
    logistic_tags: Optional[List[str]]
    content_flags: Optional[List[str]]
    publication_date: str
    region_availability: Optional[str]
    partition_id: int
    deputy_id: str
    quality: float
    nested_rating: Optional[List[GoodsCardNestedRatingItem]]
    nested_filters: Optional[List[GoodsCardNestedFilter]]
    
    class Config:
        extra = Extra.forbid
    
    
class OrderSearchItemItemsBox(BaseModel):
    box_index: str
    box_code: str
    class Config:
        alias_generator = to_camel
        
    
class OrderSearchItemItemsDiscount(BaseModel):
    discount_type: str
    discount_description: str
    discount_amount: int
    
    class Config:
        alias_generator = to_camel
    
class OrderSearchItemCustomer(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    
    class Config:
        alias_generator = to_camel


class OrderSearchItemItems(BaseModel):
    # goods_id: str = Field(..., alias='goodsId')
    is_cancelation_pending: bool
    item_index: str
    status: str
    sub_status: Optional[str]
    price: int
    final_price: int
    discounts: list[Optional[OrderSearchItemItemsDiscount]]
    quantity: int
    offer_id: str
    goods_id: str
    digital_mark: Optional[str]
    goods_data: OrderSearchItemItemsGoodsData
    boxes: Optional[list[Optional[OrderSearchItemItemsBox]]]
    goods_card: OrderSearchItemItemsGoodsCard
    
    class Config:
        alias_generator = to_camel
    


class OrderSearchItem(BaseModel):
    shipment_id: str
    order_code: Optional[str]
    shipment_is_changeable: bool
    confirmed_time_limit: Optional[str]
    packing_time_limit: Optional[str]
    shipping_time_limit: Optional[str]
    shipment_date_from: Optional[str]
    shipment_date_to: Optional[str]
    delivery_id: str
    customer_full_name: Optional[str]
    customer_address: Optional[str]
    shipping_point: str
    shipment_date_shift: bool
    creation_date: str
    delivery_date: str
    delivery_date_from: str
    delivery_date_to: str
    reserve_expiration_date: Optional[str]
    items: list[OrderSearchItemItems]
    delivery_method_id: Optional[str]
    service_scheme: str
    customer: OrderSearchItemCustomer
    deposited_amount: Optional[float]

    class Config:
        alias_generator = to_camel

    def to_dict(self, merchant_id: int) -> dict:
        def get_order_uid(order_schema: dict) -> str:
            return (
                '-'.join([
                    str(merchant_id),
                    str(order_schema.get('shipment_id'))
                ])
            )
            
        def get_catalog_item_id(merchant_offer_id: str) -> str:
            return (
                '-'.join([
                    str(merchant_id),
                    str(merchant_offer_id)
                ])
            )

        def get_order_main(order_schema: dict) -> dict:
            req_fields: list[str] = [i for i in sbermm_models.Order.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in order_schema.items() if k in req_fields}
            out_model['uid'] = get_order_uid(order_schema=order_schema)
            out_model['merchant_id'] = int(merchant_id)
            return out_model
        
        def get_order_customer(order_schema: dict) -> dict:
            if not order_schema.get('customer'):
                return (0, None)

            req_fields: list[str] = [i for i in sbermm_models.OrderCustomer.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in order_schema.get('customer').items() if k in req_fields}
            out_model['order_uid'] = get_order_uid(order_schema=order_schema)
            return (1, out_model)
        
        def get_order_item(order_schema: dict) -> dict:
            # def add_discounts(disc: dict) -> list[OrderSearchItemItemsDiscount]:
            
            if not order_schema.get('items'):
                return (0, None)

            item_container = []
            for i, item_entry in enumerate(order_schema.get('items')):
                discounts: list[dict] = []
                data_goods: list[dict] = []
                req_fields: list[str] = [i for i in sbermm_models.OrderItem.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in item_entry.items() if k in req_fields}
                out_model['order_uid'] = get_order_uid(order_schema=order_schema)
                out_model['catalog_item_id'] = get_catalog_item_id(merchant_offer_id=out_model.get('offer_id'))
                out_model['order_position_id'] = '-'.join([
                    order_schema.get('shipment_id'),
                    out_model.get('offer_id'),
                    str(i + 1)
                ])
                
                if item_entry.get('discounts'):
                    for discount in item_entry.get('discounts'):
                        discount_req_fields: list[str] = [i for i in sbermm_models.OrderItemDiscount.__dict__ if not i.startswith('_')]
                        out_discount_model: dict = {k: v for k, v in discount.items() if k in discount_req_fields}
                        out_discount_model['order_position_id'] = out_model['order_position_id']
                        discounts.append(out_discount_model)
                
                if item_entry.get('goods_data'):
                    goods_data_req_fields: list[str] = [i for i in sbermm_models.OrderItemGoodsData.__dict__ if not i.startswith('_')]
                    out_goods_data_model: dict = {k: v for k, v in item_entry.get('goods_data').items() if k in goods_data_req_fields}
                    out_goods_data_model['order_position_id'] = out_model['order_position_id']
                    data_goods = out_goods_data_model
                    
                out_model['discounts'] = discounts
                out_model['goods_data'] = data_goods
                item_container.append(out_model)
            return (1, item_container)
        
        

        new_repr = {}
        new_repr['order_main'] = get_order_main(self.dict())
        new_repr['order_customer'] = get_order_customer(self.dict())
        new_repr['order_items'] = get_order_item(self.dict())

        return new_repr

