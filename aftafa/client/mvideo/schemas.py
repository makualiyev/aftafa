from enum import Enum
import typing as tp

from pydantic import BaseModel

from aftafa.utils.helpers import to_camel

class LifeCycleStatusEnum(str, Enum):
    """Enum type for the tax system field of the customer order model"""
    VALIDATION_IN_PROGRESS = 'VALIDATION_IN_PROGRESS'
    UNPUBLISHED_CHANGES = 'UNPUBLISHED_CHANGES'
    VALIDATION_PASSED = 'VALIDATION_PASSED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    PUBLISHED = 'PUBLISHED'
    DRAFT = 'DRAFT'
    CHANGES_IN_VALIDATION = 'CHANGES_IN_VALIDATION'
    CHANGES_FAILED = 'CHANGES_FAILED'


class OrderStatusEnum(str, Enum):
    """Enum type for the status of the customer order model"""
    CREATED = 'CREATED'
    UNLOADING_COMPLETED = 'UNLOADING_COMPLETED'
    UNLOADING_START = 'UNLOADING_START'
    PREPARING_FOR_UNLOADING = 'PREPARING_FOR_UNLOADING'
    VERIFICATION_OF_DELIVERY_DOCUMENTS = 'VERIFICATION_OF_DELIVERY_DOCUMENTS'
    DOCUMENT_VERIFICATION_COMPLETED = 'DOCUMENT_VERIFICATION_COMPLETED'


class GetCatalogResponseContentElementPricesPriceEntryChangeHistory(BaseModel):
    date: str
    price: int
    promo_price: tp.Optional[int]
    currency: str
    date_start: str
    date_end: str

    class Config:
        alias_generator = to_camel


class GetCatalogResponseContentElementPricesPriceEntry(BaseModel):
    uid: str
    material_code: str
    price_type: str                                                      # TODO: Enum
    price: int                                                          # TODO: maybe float?
    promo_price: tp.Optional[int]
    currency: str                                                       # TODO: Enum?
    date_start: str
    date_end: str
    export_status: str                                                   # TODO: Enum?
    approval_status: str                                                 # TODO: Enum?
    change_history: tp.Optional[list[GetCatalogResponseContentElementPricesPriceEntryChangeHistory]]
    market_price_status: tp.Optional[str]                                              # TODO: Enum?

    class Config:
        alias_generator = to_camel


class GetCatalogResponseContentElementPrices(BaseModel):
    current_price: tp.Optional[GetCatalogResponseContentElementPricesPriceEntry]
    prices: tp.Optional[list[GetCatalogResponseContentElementPricesPriceEntry]]

    class Config:
        alias_generator = to_camel





class GetCatalogResponseContentElementStocksStockEntryHistory(BaseModel):
    unit: str
    quantity_delta: float
    date: str

    class Config:
        alias_generator = to_camel


class GetCatalogResponseContentElementStocksStockEntry(BaseModel):
    material_code: str
    warehouse_code: str                                                      # TODO: Enum
    quantity: float
    reserved: float
    available: float
    unit: str
    date_start: tp.Optional[str]
    date_end: tp.Optional[str]
    history: tp.Optional[list[GetCatalogResponseContentElementStocksStockEntryHistory]]

    class Config:
        alias_generator = to_camel



class  GetCatalogResponseContentElementStocks(BaseModel):
    current_stock: tp.Optional[GetCatalogResponseContentElementStocksStockEntry]
    stocks: tp.Optional[list[GetCatalogResponseContentElementStocksStockEntry]]

    class Config:
        alias_generator = to_camel


class GetCatalogResponseContentElement(BaseModel):
    supplier_code: str
    supplier_name: str
    group_name: str
    name: tp.Optional[str]
    barcode: tp.Optional[str]
    brand_name: tp.Optional[str]
    brand_id: tp.Optional[str]
    commission: tp.Optional[float]
    material_model_name: tp.Optional[str]
    material_account_name: tp.Optional[str]
    supplier_material_number: tp.Optional[str]
    retail_network_mvideo: bool
    retail_network_eldorado: bool
    group_id: str
    material_number: str
    sap_code_eldorado: tp.Optional[str]
    product_type: str
    life_cycle_status: tp.Optional[LifeCycleStatusEnum]
    created_date: str
    manufacturer_code: tp.Optional[str]
    main_image: tp.Optional[str]
    unit: tp.Optional[str]
    upload_id: tp.Optional[str]
    review_status: tp.Optional[str]
    archived: bool
    prices: tp.Optional[GetCatalogResponseContentElementPrices]
    last_date_validation: tp.Optional[str]
    link_eldorado: tp.Optional[str]
    link_mvideo: tp.Optional[str]
    publication_date: tp.Optional[str]
    stocks: tp.Optional[GetCatalogResponseContentElementStocks]

    class Config:
        alias_generator = to_camel


class GetCatalogResponse(BaseModel):
    total_elements: int
    pages: int
    content: list[GetCatalogResponseContentElement]

    class Config:
        alias_generator = to_camel

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
class GetOrdersResponseContentElement(BaseModel):
    uid: str
    number: str
    currency: str
    consignment: str
    delivery_location: str
    total_quantity: int
    total_sum: int
    date_create: str
    delivery_date: str
    type_of_sale: str
    total_gross_weight: float
    total_package_volume: float
    status: str
    last_import_date: tp.Optional[str]
    payment_terms: tp.Optional[str]
    supplier_code: tp.Optional[str]
    total_entry: tp.Optional[int]
    total_tax: tp.Optional[float]
    version: tp.Optional[int]

    class Config:
        alias_generator = to_camel


class GetOrdersResponse(BaseModel):
    total_elements: int
    count: int
    content: list[GetOrdersResponseContentElement]

    class Config:
        alias_generator = to_camel

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
class GetOrderEntriesResponseContentElement(BaseModel):
    uid: str
    material_code: str
    material_supplier_code: str
    group_code: str
    material_name: str
    gross_weight: int
    package_volume: int
    purchase_price: int
    quantity: int
    purchase_sum: int
    assignment: tp.Optional[str]
    consignment: str
    delivery_date: tp.Optional[str]
    delivery_location: tp.Optional[str]
    ean: tp.Optional[str]
    last_import_date: tp.Optional[str]
    net_weight: tp.Optional[float]
    order_uid: str
    status: str
    tax: float
    unit: tp.Optional[str]
    unit_volume: tp.Optional[str]
    vat_rate: tp.Optional[str]
    version: int
    weight_unit: tp.Optional[str]

    class Config:
        alias_generator = to_camel


class GetOrderEntriesResponse(BaseModel):
    total_elements: int
    count: int
    content: list[GetOrderEntriesResponseContentElement]

    class Config:
        alias_generator = to_camel

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
class GetProductMovementsResponseContentElement(BaseModel):
    uid: str
    product_type: str
    zmaterial: str
    material_name: str
    state: str
    status: str
    zplant: str
    brand: str
    material_group: str
    object_type: str
    city: str
    street_address: str
    qty: int

    class Config:
        alias_generator = to_camel


class GetProductMovementsResponse(BaseModel):
    total_elements: int
    pages: int
    content: list[GetProductMovementsResponseContentElement]

    class Config:
        alias_generator = to_camel