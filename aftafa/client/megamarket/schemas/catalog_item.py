from __future__ import annotations
from typing import List, Dict, Union, Optional

from pydantic import BaseModel, Field, constr

import aftafa.client.megamarket.models as sbermm_models
from aftafa.utils.helpers import to_camel


MerchantIdNumbers = constr(regex=r'^[0-9]+$')

class OutletItemValue(BaseModel):
    id: str
    instock: str


class OutletItem(BaseModel):
    field_: OutletItemValue = Field(..., alias='$')


class Outlets(BaseModel):
    outlet: List[OutletItem]


class ParamItemField(BaseModel):
    name: str


class ParamItem(BaseModel):
    field_: ParamItemField = Field(..., alias='$')
    field_text: str = Field(..., alias='$text')


class BidField(BaseModel):
    id: Optional[str]
    bid: Optional[str]
    available: str


class Category(BaseModel):
    id: str
    name: str
    parent_id: Optional[str]

    class Config:
        alias_generator = to_camel


class Cleared(BaseModel):
    cleared_offer_vendor_code: str
    cleared_offer_vendor: str
    cleared_offer_name: str
    cleared_merchant_offer_name: str
    cleared_merchant_offer_id: str


class MatchingCardItem(BaseModel):
    category_id: Optional[str]
    categories: Optional[List[Category]]
    name: str
    prefix: Optional[str]
    model: Optional[str]
    vendor: str
    mpn: Optional[str]
    description: Optional[str]
    price: Optional[int]
    vat: Optional[str]
    country_of_origin: Optional[str]
    barcodes: Optional[List[str]]
    attributes: Optional[List[ParamItem]]
    url: Optional[str]

    class Config:
        alias_generator = to_camel


class MerchantGoods(BaseModel):
    """
    Merchant goods entry
    """
    merchant_offer_id: str
    manual_price: Optional[str]
    feed_price: Optional[str]
    delivery: Optional[bool]
    pickup: Optional[bool]
    store: Optional[bool]
    url: Optional[str]
    currency_id: Optional[str]
    category_id: Optional[str]
    outlets: Optional[Outlets]
    picture: Optional[str]
    name: str
    barcode: Optional[List[str]]
    vendor: str
    description: Optional[str]
    price: int
    param: Optional[List[ParamItem]]
    bid_field: Optional[BidField] = Field(None, alias='$')
    merchant_offer_name: str
    vendor_code: Optional[str]
    categories: Optional[List[Category]]
    category_path: Optional[str]
    cleared: Optional[Cleared]
    matching_card: List[MatchingCardItem]

    class Config:
        alias_generator = to_camel


class MerchantRate(BaseModel):
    service_scheme: Optional[str]
    rate: Optional[int]
    min_fee: Optional[int]

    class Config:
        alias_generator = to_camel


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


class Extra(BaseModel):
    bpg2_competitors: Optional[int]


class PriceHistoryItem(BaseModel):
    point_id: int
    point_name: str
    point_value: int


class PriceAdjustment(BaseModel):
    type: str
    amount: int


class Price(BaseModel):
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
    extra: Optional[Extra]
    price_history: List[PriceHistoryItem]
    delivery_date: str
    price_change_percentage: Optional[float]
    price_adjustments: List[PriceAdjustment]


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


class SuggestedGoodsCategory(BaseModel):
    master: List[List[str]]
    web: List[List[str]]
    sandbox: Optional[List[List[str]]]


class SuggestedGoodsAttribute(BaseModel):
    name: str
    group: str
    sequence: int
    purpose: Optional[List[str]]
    units: str
    type: str
    feature_description: str
    value: List[str]


class SuggestedGoodsDocument(BaseModel):
    document_link: str


class Image(BaseModel):
    image_link: str
    image_order: str


class Box(BaseModel):
    box: str
    packaging_unit: str
    width: int
    height: int
    length: int
    weight_unit: str
    weight: int


class SuggestedGoodsExtra(BaseModel):
    attributes_on_page: int
    is_attributes_over_page: int


class DeputySelector(BaseModel):
    name: Optional[str]
    control_type: Optional[str]
    value: Optional[str]


class Deputy(BaseModel):
    rule_id: Optional[str]
    deputy_id: Optional[str]
    fraction_id: Optional[str]
    selector_plp: Optional[Union[DeputySelector, list[DeputySelector]]]
    selector_pdp: Optional[Union[DeputySelector, list[DeputySelector]]]


class NestedRatingItem(BaseModel):
    collection_id: str
    value: int
    value_bi: Optional[int]


class NestedFilter(BaseModel):
    id: str
    string_values: Optional[List[str]]
    float_values: Optional[List[int]]


class SuggestedGoods(BaseModel):
    goods_id: str = Field(..., alias='goodsId')
    rate: Optional[int]
    min_fee: Optional[str]
    date_activate: Optional[str] = Field(..., alias='dateActivate')
    merchant_rates: List[MerchantRate] = Field(..., alias='merchantRates')
    item_id: str
    purpose: List[str]
    display_on_web: int
    single_offer_card: bool
    long_web_name: str
    short_web_name: str
    prices: Price
    offers_v2: Optional[List[OffersV2Item]]
    brand: str
    brand_slug: str
    badges: Optional[List[str]]
    category: Optional[SuggestedGoodsCategory]
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
    attributes: List[SuggestedGoodsAttribute]
    video: str
    images: List[Image]
    thumbnail: str
    documents: Optional[List[SuggestedGoodsDocument]]
    boxes: Optional[List[Box]]
    flags: Optional[List[str]]
    collections: List[int]
    main_web_collection_id: int
    update_at: str
    url: str
    reviews_count: int
    reviews_rating: int
    reviews_show: int
    extra: SuggestedGoodsExtra
    successor: Optional[str]
    deputy: Deputy
    logistic_tags: Optional[List[str]]
    content_flags: Optional[List[str]]
    publication_date: str
    region_availability: Optional[str]
    partition_id: int
    deputy_id: str
    quality: float
    nested_rating: Optional[List[NestedRatingItem]]
    nested_filters: Optional[List[NestedFilter]]


class CatalogItem(BaseModel):
    merchant_id: int
    merchant_goods: MerchantGoods
    rn: str
    suggested_goods: SuggestedGoods
    type_confirmation: Optional[str]
    date_confirmation: str
    publication_status: str
    publication_status_humanized: str
    publication_status_color: str
    can_unlock: bool
    lock_description: Optional[bool]
    quantity: Optional[int]

    class Config:
        alias_generator = to_camel

    def to_dict(self) -> dict:
        def get_catalog_item_id(catalog_item_schema: dict) -> str:
            return (
                '-'.join([
                    str(catalog_item_schema['merchant_id']),
                    str(catalog_item_schema.get('merchant_goods').get('merchant_offer_id'))
                ])
            )


        def get_catalog_item(catalog_item_schema: dict) -> dict:
            req_fields: list[str] = [i for i in sbermm_models.CatalogItem.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in catalog_item_schema.items() if k in req_fields}
            out_model['catalog_item_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
            if not out_model['quantity']:
                out_model['quantity'] = 0
            return out_model
        
        def get_merchant_goods(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('merchant_goods'):
                return (0, None)

            req_fields: list[str] = [i for i in sbermm_models.MerchantGoods.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in catalog_item_schema.get('merchant_goods').items() if k in req_fields}
            out_model['catalog_item_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
            
            if not out_model['barcode']:
                out_model['barcode'] = ''
            out_model['barcode'] = out_model['barcode'][0] if len(out_model['barcode']) > 0 else ''
            
            return (1, out_model)
        
        def get_merchant_goods_outlets(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('merchant_goods').get('outlets'):
                return (0, None)

            if not catalog_item_schema.get('merchant_goods').get('outlets').get('outlet'):
                return (0, None)

            outlet_container = []
            for outlet_entry in catalog_item_schema.get('merchant_goods').get('outlets').get('outlet'):
                req_fields: list[str] = [i for i in sbermm_models.MerchantGoodsOutlets.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in outlet_entry.get('field_').items() if k in req_fields}
                out_model['outlet_id'] = out_model['id']
                out_model['merchant_offer_id'] = catalog_item_schema.get('merchant_goods').get('merchant_offer_id')
                out_model.pop('id')
                out_model['merchant_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                outlet_container.append(out_model)
            return (1, outlet_container)
        
        def get_suggested_goods(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('suggested_goods'):
                return (0, None)
            req_fields: list[str] = [i for i in sbermm_models.SuggestedGoods.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in catalog_item_schema.get('suggested_goods').items() if k in req_fields}
            out_model['gtin'] = ';'.join(catalog_item_schema.get('suggested_goods')['gtins']) if catalog_item_schema.get('suggested_goods')['gtins'] else ''
            out_model['flags'] = ';'.join(out_model['flags']) if out_model['flags'] else ''
            out_model['catalog_item_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
            master_part = catalog_item_schema.get('suggested_goods').get('category').get('master')
            if isinstance(master_part, list) and len(master_part) == 1:
                out_model['category_master'] = {len(i): i for i in master_part[0]}.get(max(len(i) for i in master_part[0]))
            else:
                print(f"This good has different category_master in suggestedGoods -> {out_model['catalog_item_id']} \n here it is => {master_part} \n")
            return (1, out_model)
        
        def get_suggested_goods_merchant_rates(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('suggested_goods').get('merchant_rates'):
                return (0, None)
            merchant_rates_container = []
            for merchant_rate_entry in catalog_item_schema.get('suggested_goods').get('merchant_rates'):
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsMerchantRates.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in merchant_rate_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                # out_model['merchant_offer_id'] = catalog_item_schema.get('merchant_goods').get('merchant_offer_id')
                # out_model.pop('id')
                merchant_rates_container.append(out_model)
            return (1, merchant_rates_container)
        
        def get_suggested_goods_prices(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('suggested_goods').get('prices'):
                return (0, None)
            
            req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPrices.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in catalog_item_schema.get('suggested_goods').get('prices').items() if k in req_fields}
            out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
            return (1, out_model)
        
        def get_suggested_goods_prices_favorite_offer(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('favorite_offer')
            
            if not target_schema:
                return (0, None)

            req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesFavoriteOffer.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in target_schema.items() if k in req_fields}
            if all(not v for k, v in out_model.items()):
                return (0, None)
            out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')

            return (1, out_model)

        def get_suggested_goods_prices_offers(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('offers')
            if not target_schema:
                return (0, None)
            prices_offers_container = []
            for prices_offers_entry in target_schema:
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesOffers.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in prices_offers_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                out_model['suggested_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                prices_offers_container.append(out_model)
            return (1, prices_offers_container)
        
        # def get_suggested_goods_prices_bonus(catalog_item_schema: dict) -> dict:
        #     target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('bonus')
            
        #     if not target_schema:
        #         return (0, None)
            
        #     req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesBonus.__dict__ if not i.startswith('_')]
        #     out_model: dict = {k: v for k, v in target_schema.items() if k in req_fields}
        #     out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
        #     return (1, out_model)
        
        def get_suggested_goods_prices_bonus_merchant_bonus(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('bonus').get('merchant_bonus')
            if not target_schema:
                return (0, None)
            prices_bonus_merchant_bonus_container = []
            for prices_bonus_merchant_bonus_key, prices_bonus_merchant_bonus_entry in target_schema.items():
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in prices_bonus_merchant_bonus_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                out_model['suggested_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                prices_bonus_merchant_bonus_container.append(out_model)
            return (1, prices_bonus_merchant_bonus_container)
        
        def get_suggested_goods_prices_price_history(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('price_history')
            if not target_schema:
                return (0, None)
            prices_price_history_container = []
            for prices_price_history_entry in target_schema:
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesPriceHistory.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in prices_price_history_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                out_model['suggested_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                prices_price_history_container.append(out_model)
            return (1, prices_price_history_container)
        
        def get_suggested_goods_prices_price_adjustments(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('prices').get('price_adjustments')
            if not target_schema:
                return (0, None)
            prices_price_adjustments_container = []
            for prices_price_adjustments_entry in target_schema:
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesPriceAdjustments.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in prices_price_adjustments_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                out_model['suggested_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                prices_price_adjustments_container.append(out_model)
            return (1, prices_price_adjustments_container)
        
        def get_suggested_goods_offers_v2(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('offers_v2')
            if not target_schema:
                return (0, None)
            offers_v2_container = []
            for offers_v2_entry in target_schema:
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsOffersV2.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in offers_v2_entry.items() if k in req_fields}
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                out_model['suggested_goods_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
                offers_v2_container.append(out_model)
            return (1, offers_v2_container)
        
        def get_suggested_goods_box(catalog_item_schema: dict) -> dict:
            target_schema = catalog_item_schema.get('suggested_goods').get('boxes')
            if not target_schema:
                return (0, None)
            boxes_container = []
            for boxes_entry in target_schema:
                req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsBox.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in boxes_entry.items() if k in req_fields}
                out_model['box_id'] = boxes_entry['box']
                out_model['goods_id'] = catalog_item_schema.get('suggested_goods').get('goods_id')
                
                boxes_container.append(out_model)
            return (1, boxes_container)
        

        new_repr = {}
        new_repr['main_catalog_item'] = get_catalog_item(self.dict())
        new_repr['merchant_goods'] = get_merchant_goods(self.dict())
        new_repr['merchant_goods_outlets'] = get_merchant_goods_outlets(self.dict())
        new_repr['suggested_goods'] = get_suggested_goods(self.dict())
        new_repr['suggested_goods_merchant_rates'] = get_suggested_goods_merchant_rates(self.dict())
        new_repr['suggested_goods_prices'] = get_suggested_goods_prices(self.dict())
        new_repr['suggested_goods_prices_favorite_offer'] = get_suggested_goods_prices_favorite_offer(self.dict())
        new_repr['suggested_goods_prices_offers'] = get_suggested_goods_prices_offers(self.dict())
        # new_repr['suggested_goods_prices_bonus'] = get_suggested_goods_prices_bonus(self.dict())
        new_repr['suggested_goods_prices_bonus_merchant_bonus'] = get_suggested_goods_prices_bonus_merchant_bonus(self.dict())
        new_repr['suggested_goods_prices_price_history'] = get_suggested_goods_prices_price_history(self.dict())
        new_repr['suggested_goods_prices_price_adjustments'] = get_suggested_goods_prices_price_adjustments(self.dict())
        new_repr['suggested_goods_offers_v2'] = get_suggested_goods_offers_v2(self.dict())
        new_repr['suggested_goods_box'] = get_suggested_goods_box(self.dict())

        return new_repr

