from __future__ import annotations
from typing import List, Dict, Union, Optional

from pydantic import BaseModel, Field, constr, Extra

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
    category_id: str
    outlets: Outlets
    picture: Optional[str]
    name: str
    barcode: List[str]
    vendor: str
    description: Optional[str]
    price: int
    param: Optional[List[ParamItem]]
    bid_field: BidField = Field(..., alias='$')
    merchant_offer_name: str
    vendor_code: str
    categories: List[Category]
    category_path: str
    cleared: Optional[Cleared]
    matching_card: List[MatchingCardItem]

    class Config:
        alias_generator = to_camel


class SuggestedGoods(BaseModel):
    goods_id: Optional[str] = Field(..., alias='goodsId')
    weight: Optional[str]
    matchedMerchantOfferId: Optional[str]
    
    class Config:
        extra = Extra.forbid


class SuggestListItem(BaseModel):
    merchant_id: int
    merchant_goods: MerchantGoods
    rn: str
    suggested_goods: SuggestedGoods
    reason_not_matched: Optional[str]

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
            out_model['publication_status'] = 'ASSORTMENT_NO_MATCH'
            out_model['publication_status_humanized'] = 'Соответствие не найдено'
            out_model['can_unlock'] = False
            out_model['quantity'] = 0
            
            return out_model
        
        def get_merchant_goods(catalog_item_schema: dict) -> dict:
            if not catalog_item_schema.get('merchant_goods'):
                return (0, None)

            req_fields: list[str] = [i for i in sbermm_models.MerchantGoods.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in catalog_item_schema.get('merchant_goods').items() if k in req_fields}
            out_model['catalog_item_id'] = get_catalog_item_id(catalog_item_schema=catalog_item_schema)
            out_model['barcode'] = out_model['barcode'][0] if len(out_model['barcode']) > 0 else ''
            
            return (1, out_model)
        
        def get_merchant_goods_outlets(catalog_item_schema: dict) -> dict:
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
        

        new_repr = {}
        new_repr['main_catalog_item'] = get_catalog_item(self.dict())
        new_repr['merchant_goods'] = get_merchant_goods(self.dict())
        new_repr['merchant_goods_outlets'] = get_merchant_goods_outlets(self.dict())

        return new_repr

