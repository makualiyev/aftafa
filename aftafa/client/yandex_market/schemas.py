from typing import Optional

from pydantic import BaseModel, Field

from aftafa.utils.helpers import to_camel, to_lower
import aftafa.client.yandex_market.models as ya_models
from aftafa.client.yandex_market.enums import *


class CampaignDTO(BaseModel):
    domain: Optional[str]                                                           # URL магазина
    id: int                                                                         # Идентификатор кампании
    client_id: int                                                                  # Идентификатор плательщика в Яндекс Балансе

    class Config:
        alias_generator = to_camel


class FlippingPagerDTO(BaseModel):
    total: int                                                                      # Сколько всего найдено элементов
    from_: int = Field(alias='from')                                                # Начальный номер найденного элемента на странице
    to: int                                                                         # Конечный номер найденного элемента на странице
    currentPage: int                                                                # Текущая страница
    pagesCount: int                                                                 # Общее количество страниц
    pageSize: int                                                                   # Размер страницы

class GetCampaignsResponse(BaseModel):
    campaigns: list[CampaignDTO]
    pager: FlippingPagerDTO


#          ---------          ---------          ---------          ---------          ---------            ---------           ---------
class CampaignSettingsTimePeriodDTO(BaseModel):
    fromDate: str
    toDate: str


class CampaignSettingsScheduleDTO(BaseModel):
    availableOnHolidays: bool
    customHolidays: list[str]
    customWorkingDays: list[str]
    period: CampaignSettingsTimePeriodDTO
    totalHolidays: list[str]
    weeklyHolidays: list[int]


class CampaignSettingsDeliveryDTO(BaseModel):
    schedule: CampaignSettingsScheduleDTO


class CampaignSettingsLocalRegionDTO(BaseModel):
    id: int
    name: str
    type: RegionType
    deliveryOptionsSource: CampaignSettingsScheduleSourceType
    delivery: CampaignSettingsDeliveryDTO


class CampaignSettingsDTO(BaseModel):
    countryRegion: int
    shopName: Optional[str]
    showInContext: Optional[bool]
    showInPremium: Optional[bool]
    useOpenStat: bool
    localRegion: CampaignSettingsLocalRegionDTO


class GetCampaignsSettingsResponse(BaseModel):
    settings: CampaignSettingsDTO


# ---------          ---------          ---------         ---------          ---------           ---------            ---------    
#          ---------          ---------          ---------          ---------          ---------            ---------           ---------
class ScrollingPagerDTO(BaseModel):
    nextPageToken: Optional[str]
    prevPageToken: Optional[str]


class PriceDTO(BaseModel):
    value: Optional[float]
    discount_base: Optional[float]
    currency_id: Optional[str]
    vat: Optional[int]

    class Config:
        alias_generator = to_camel


class OfferPriceDTO(BaseModel):
    id: int

class OfferPriceResponseDTO(BaseModel):
    id: str
    feed: Optional[OfferPriceDTO]
    price: PriceDTO
    market_sku: Optional[int]
    updated_at: str

    class Config:
        alias_generator = to_camel


class OfferPriceListResponseDTO(BaseModel):
    offers: list[OfferPriceResponseDTO]
    paging: Optional[ScrollingPagerDTO]
    total: int

class GetOfferPricesResponse(BaseModel):
    # status: Literal['OK', 'ERROR']
    status: str
    result: OfferPriceListResponseDTO


# ---------          ---------          ---------         ---------          ---------           ---------            ---------    
#          ---------          ---------          ---------          ---------          ---------            ---------           ---------
class WarehouseDTO(BaseModel):
    id: int
    name: str
    campaignId: int


class WarehouseGroupDTO(BaseModel):
    name: str
    mainWarehouse: WarehouseDTO
    warehouses: list[WarehouseDTO]


class WarehousesDTO(BaseModel):
    warehouses: list[WarehouseDTO]
    warehouseGroups: list[Optional[WarehouseGroupDTO]]


class GetWarehousesResponse(BaseModel):
    # status: Literal['OK', 'ERROR']
    status: ResponseStatusEnum
    result: WarehousesDTO

# ---------          ---------          ---------         ---------          ---------           ---------            ---------    
#          ---------          ---------          ---------          ---------          ---------            ---------           ---------

class OfferWeightDimensionsDTO(BaseModel):
    length: float
    width: float
    height: float
    weight: Optional[float]


class Hidings(BaseModel):
    type: str | None
    code: str | None
    message: str | None
    comment: str | None


class LifeTime(BaseModel):  # FIXME: mb change the name of this class
    timePeriod: int
    timeUnit: TimeUnitEnum
    comment: Optional[str]


class ResponseError(BaseModel):
    code: str
    message: str


class ProcessingStateNote(BaseModel):
    type: ProcessingStateNoteTypeEnum
    payload: Optional[str]


class OfferProcessingStateDTO(BaseModel):
    status: ProcessingStateEnum
    notes: Optional[list[ProcessingStateNote]]


class MappingsOfferDTO(BaseModel):
    """ "
    The same thing as a product or a card
    """

    offer_id: str
    name: Optional[str]
    category: Optional[str]
    manufacturer: Optional[str]
    manufacturer_countries: Optional[list[str]]
    weight_dimensions: OfferWeightDimensionsDTO
    urls: Optional[list[str]]
    pictures: Optional[list[str]]
    vendor: Optional[str]
    vendor_code: Optional[str]
    barcodes: Optional[list[str]]
    description: Optional[str]
    shelf_life: Optional[LifeTime]
    life_time: Optional[LifeTime]
    guarantee_period: Optional[LifeTime]
    customs_commodity_codes: Optional[list[str]]
    certificate: Optional[str]
    availability: Optional[OfferAvailabilityStatusType]
    transport_unit_size: Optional[int]
    min_shipment: Optional[int]
    quantum_of_supply: Optional[int]
    supply_schedule_days: Optional[
        list[
            str
        ]
    ]
    delivery_duration_days: Optional[int]
    box_count: Optional[int]
    shelf_life_days: Optional[int]
    lifeTime_days: Optional[int]
    guarantee_period_days: Optional[int]
    processing_state: Optional[OfferProcessingStateDTO]

    class Config:
        alias_generator = to_camel


class OfferMappingDTO(BaseModel):
    marketSku: Optional[int]
    marketSkuName: Optional[str]
    marketModelId: Optional[int]
    marketModelName: Optional[str]
    modelId: Optional[int]
    # categoryId: int
    marketCategoryId: int
    marketCategoryName: Optional[str]


class OfferMappingEntryDTO(BaseModel):

    offer: MappingsOfferDTO
    mapping: Optional[OfferMappingDTO]
    awaitingModerationMapping: Optional[OfferMappingDTO]
    rejectedMapping: Optional[OfferMappingDTO]


class OfferMappingEntryResultPaging(BaseModel):
    nextPageToken: Optional[str]


class OfferMappingEntriesDTO(BaseModel):
    paging: Optional[ScrollingPagerDTO]
    offerMappings: list[OfferMappingEntryDTO]


class GetOfferMappingResponse(BaseModel):
    status: ResponseStatusEnum
    result: Optional[OfferMappingEntriesDTO]



class PostBusinessOfferMappingsResponse(BaseModel):
    status: ResponseStatusEnum
    result: Optional[OfferMappingEntriesDTO]


# ---------          ---------          ---------         ---------          ---------           ---------            ---------    
#          ---------          ---------          ---------          ---------          ---------            ---------           ---------
class ShopSkuWarehouseStocks(BaseModel):
    type: WarehouseStockTypeEnum
    count: int


class ShopSkuWarehouses(BaseModel):
    id: int
    name: str
    stocks: list[ShopSkuWarehouseStocks]


class ShopSkuStorageInclusion(BaseModel):
    type: ShopSkuStorageInclusionTypeEnum
    count: int


class ShopSkuStorage(BaseModel):
    type: ShopSkuStorageTypeEnum
    count: int
    inclusions: ShopSkuStorageInclusion


class TariffEntry(BaseModel):
    type: TariffEntryEnum
    percent: Optional[float]
    amount: Optional[float]


class ShopSku(BaseModel):
    """
    The same thing as a product or a card
    """

    shopSku: str
    marketSku: Optional[int]
    name: Optional[str]
    price: Optional[float]
    categoryId: Optional[int]
    categoryName: Optional[str]
    weightDimensions: OfferWeightDimensionsDTO
    hidings: Optional[list[Hidings]]
    warehouses: Optional[list[ShopSkuWarehouses]]
    storage: Optional[ShopSkuStorage]
    tariffs: Optional[list[TariffEntry]]
    pictures: Optional[list[str]]


# ---------          ---------          ---------         ---------          ---------           ---------            ---------          ---------          ---------          ---------         ---------          ---------           ---------            ---------    
#          ---------          ---------          ---------          ---------          ---------            ---------           ---------          ---------          ---------          ---------          ---------          ---------            ---------           ---------
class OrdersStatsDeliveryRegionDTO(BaseModel):
    id: int
    name: str


class OrdersStatsPriceDTO(BaseModel):
    type: OrderEntryItemPriceTypeEnum
    cost_per_item: float
    total: float

    class Config:
        alias_generator = to_camel


class OrdersStatsWarehouseDTO(BaseModel):
    id: int
    name: str


class OrdersStatsDetailsDTO(BaseModel):
    item_status: Optional[str]
    item_count: Optional[int]
    update_date: Optional[str]
    stock_type: Optional[str]

    class Config:
        alias_generator = to_camel


# class OrderEntryInitialItems(BaseModel):
#     offerName: str
#     marketSku: int
#     shopSku: str
#     initialCount: int

class OrdersStatsPaymentOrderDTO(BaseModel):
        id: str
        date: Optional[str]


class OrdersStatsPaymentDTO(BaseModel):
    id: str
    date: Optional[str]
    type: Optional[str]
    source: Optional[str]
    total: float
    payment_order: Optional[OrdersStatsPaymentOrderDTO]

    class Config:
        alias_generator = to_camel


class OrdersStatsCommissionDTO(BaseModel):
    type: Optional[OrderStatsCommissionsTypeEnum]
    actual: Optional[float]
    predicted: Optional[float]


class OrdersStatsItemDTO(BaseModel):
    offer_name: str
    market_sku: int
    shop_sku: str
    count: Optional[int]
    prices: Optional[list[OrdersStatsPriceDTO]]
    warehouse: Optional[OrdersStatsWarehouseDTO]
    details: Optional[list[OrdersStatsDetailsDTO]]
    cis_list: Optional[list[str]]
    initial_count: Optional[int]
    bid_fee: Optional[int]

    class Config:
        alias_generator = to_camel


class OrdersStatsOrderDTO(BaseModel):

    id: int
    creation_date: str
    status: OrderStatsStatusType
    status_update_date: str
    partner_order_id: Optional[str]
    payment_type: str
    fake: Optional[bool]
    delivery_region: Optional[OrdersStatsDeliveryRegionDTO]
    items: list[OrdersStatsItemDTO]
    initial_items: Optional[list[OrdersStatsItemDTO]]
    payments: list[OrdersStatsPaymentDTO]
    commissions: list[OrdersStatsCommissionDTO]

    class Config:
        alias_generator = to_camel

    def to_dict(self) -> dict:
        def get_main_order(order_schema: dict) -> dict:
            req_fields: list[str] = [i for i in ya_models.Order.__dict__ if not i.startswith('_')]
            out_model: dict = {k: v for k, v in order_schema.items() if k in req_fields}
            out_model['order_id'] = order_schema['id']
            out_model['delivery_region_id'] = order_schema['delivery_region']['id']
            out_model['delivery_region'] = order_schema['delivery_region']
            out_model.pop('id')
            return out_model

        def get_order_commissions(order_schema: dict) -> tuple[int, list[dict]]:
            if not order_schema.get('commissions'):
                return (0, None)
            commission_container = []
            for commission_entry in order_schema.get('commissions'):
                req_fields: list[str] = [i for i in ya_models.OrderCommissions.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in commission_entry.items() if k in req_fields}
                out_model['order_id'] = order_schema['id']
                commission_container.append(out_model)
            return (1, commission_container)

        def get_order_payments(order_schema: dict) -> tuple[int, list[dict]]:
            if not order_schema.get('payments'):
                return (0, None)
            payments_container = []
            for payments_entry in order_schema.get('payments'):
                payments_entry['payment_id'] = payments_entry['id']
                payments_entry.pop('id')
                req_fields: list[str] = [i for i in ya_models.OrderPayments.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in payments_entry.items() if k in req_fields}
                out_model['order_id'] = order_schema['id']
                payments_container.append(out_model)
            return (1, payments_container)

        def get_order_items(order_schema: dict) -> tuple[int, list[dict]]:
            if not order_schema.get('items'):
                return (0, None)
            items_container = []
            for item_entry in order_schema.get('items'):
                req_fields: list[str] = [i for i in ya_models.OrderItem.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in item_entry.items() if k in req_fields}
                out_model['order_id'] = order_schema['id']
                out_model['shop_sku'] = item_entry['shop_sku']
                out_model['warehouse'] = item_entry['warehouse']
                out_model['warehouse_id'] = item_entry['warehouse']['id']
                out_model['attrs'] = {}
                for attr in ['prices', 'details', 'cis_list']:
                    if not item_entry.get(attr):
                        out_model['attrs'][attr] = (0, None)
                        continue
                    out_model['attrs'][attr] = (1, item_entry.get(attr))
                items_container.append(out_model)
            return (1, items_container)

        def get_order_initial_items(order_schema: dict) -> tuple[int, list[dict]]:
            if not order_schema.get('initial_items'):
                return (0, None)
            items_container = []
            for item_entry in order_schema.get('items'):
                req_fields: list[str] = [i for i in ya_models.OrderItem.__dict__ if not i.startswith('_')]
                out_model: dict = {k: v for k, v in item_entry.items() if k in req_fields}
                out_model['order_id'] = order_schema['id']
                out_model['shop_sku'] = item_entry['shop_sku']
                out_model['warehouse'] = item_entry['warehouse']
                out_model['warehouse_id'] = item_entry['warehouse']['id']
                out_model['attrs'] = {}
                for attr in ['prices', 'details', 'cis_list']:
                    if not item_entry.get(attr):
                        out_model['attrs'][attr] = (0, None)
                        continue
                    out_model['attrs'][attr] = (1, item_entry.get(attr))
                items_container.append(out_model)
            return (1, items_container)
        
        new_repr = {}
        new_repr['main_order'] = get_main_order(self.dict())
        new_repr['commissions'] = get_order_commissions(self.dict())
        new_repr['payments'] = get_order_payments(self.dict())
        new_repr['items'] = get_order_items(self.dict())
        new_repr['initial_items'] = get_order_initial_items(self.dict())
        return new_repr




class ForwardScrollingPagerDTO(BaseModel):
    nextPageToken: Optional[str]


class OrdersStatsDTO(BaseModel):
    orders: Optional[list[OrdersStatsOrderDTO]]
    paging: ForwardScrollingPagerDTO


class OrderResponse(BaseModel):

    status: ResponseStatusEnum
    result: OrdersStatsDTO
    errors: Optional[list[ResponseError]]


class GenerateReportDTO(BaseModel):
    reportId: str
    estimatedGenerationTime: int


class PostStocksOnWarehousesGenerateResponse(BaseModel):
    status: ResponseStatusEnum
    result: GenerateReportDTO


class ReportInfoDTO(BaseModel):
    status: ReportStatusType
    subStatus: Optional[str]
    generationRequestedAt: str
    generationFinishedAt: Optional[str]
    file: Optional[str]
    estimatedGenerationTime: Optional[int]

class GetReportsInfoResponse(BaseModel):
    status: ResponseStatusEnum
    result: ReportInfoDTO