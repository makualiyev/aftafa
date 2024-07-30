from datetime import datetime
from typing import List, Optional, Any, Union
from enum import Enum
from itertools import chain

from pydantic import BaseModel, UUID4, Field


class GetCategoriesTree_Category(BaseModel):
    category_id : int
    title : str
    children : Optional[List['GetCategoriesTree_Category']]

class GetCategoriesTree_Response(BaseModel):
    result : List[GetCategoriesTree_Category]


class PostProductList_Product(BaseModel):
    product_id : int
    offer_id : str

class PostProductList_Response(BaseModel):
    items : List[PostProductList_Product]
    total : int

# ------------------------------------------------------------------------------------------------------        
class PostProductInfo(BaseModel):

    class productv2GetProductInfoResponseCommissions(BaseModel):
        delivery_amount : float
        min_value : float
        percent : float
        return_amount : float
        sale_schema : str
        value : float

    class productv2Status(BaseModel):

        class v2ItemError(BaseModel):
            code : str
            state : str
            level : str
            description : str
            field : str
            attribute_id : int
            attribute_name : str
            optional_description_elements : Any

        state : str
        state_failed : str
        moderate_status : str
        decline_reasons : List[str]
        validation_state : str
        state_name : str
        state_description : str
        is_failed : bool
        is_created : bool
        state_tooltip : str
        item_errors : List[v2ItemError]
        state_updated_at : datetime

    class productv2GetProductInfoResponseSource(BaseModel):
        is_enabled : bool
        sku : int
        source : str

    class productv2GetProductInfoResponseStock(BaseModel):
        coming : int
        present : int
        reserved : int

    class productv2GetProductInfoResponseVisibilityDetails(BaseModel):
        active_product : bool
        has_price : bool
        has_stock : bool

    barcode : str
    buybox_price : str
    category_id : int
    color_image : str
    commissions : Optional[List[productv2GetProductInfoResponseCommissions]]
    created_at : datetime
    id : int
    images : List[str]
    primary_image : str
    images360 : List[str]
    is_kgt: bool
    is_prepayment : Optional[bool]
    is_prepayment_allowed : Optional[bool]
    marketing_price : str
    min_ozon_price : str
    min_price : str
    name : str
    offer_id : str
    old_price : str
    premium_price : str
    price : str
    price_index : str
    recommended_price : str
    status : productv2Status
    sources : List[productv2GetProductInfoResponseSource]
    stocks : productv2GetProductInfoResponseStock
    vat : str
    visibility_details : productv2GetProductInfoResponseVisibilityDetails
    visible : bool
    volume_weight : Optional[float]

# ------------------------------------------------------------------------------------------------------

class PostProductInfoList(BaseModel):

    items : list[PostProductInfo]

# -------------------------------------------------------------------------------------------------------
class productv2GetProductAttributesResponseAttribute(BaseModel):
    class productv2GetProductAttributesResponseDictionaryValue(BaseModel):
        dictionary_value_id : int
        value : str

    attribute_id : int
    complex_id : int
    values : list[productv2GetProductAttributesResponseDictionaryValue]

class PostProductInfoAttributesList(BaseModel):
    class productv2GetProductAttributesResponseComplexAttribute(BaseModel):
        attributes : list[productv2GetProductAttributesResponseAttribute]

    class GetProductAttributesResponseImage(BaseModel):
        default : bool
        file_name : str
        index : int

    class GetProductAttributesResponseImage360(BaseModel):
        file_name : str
        index : int

    class GetProductAttributesResponsePdf(BaseModel):
        file_name : str
        index : int
        name : str

    barcode : str
    category_id : int
    color_image : str
    complex_attributes : list[productv2GetProductAttributesResponseComplexAttribute]
    depth : int
    dimension_unit : str
    height : int
    id : int
    image_group_id : str
    images : list[GetProductAttributesResponseImage]
    images360 : list[GetProductAttributesResponseImage360]
    name : str
    offer_id : str
    pdf_list : list[GetProductAttributesResponsePdf]
    weight : int
    weight_unit : str
    width : int

# -------------------------------------------------------------------------------------------------------
class GetProductRatingBySkuResponseRatingCondition(BaseModel):
    """Список условий, увеличивающих контент-рейтинг товара"""
    cost: float                                                                     # Количество баллов контент-рейтинга, которое даёт выполнение условия
    description: str                                                                # Описание условия
    fulfilled: bool                                                                 # Признак, что условие выполнено
    key: str                                                                        # Идентификатор условия


class GetProductRatingBySkuResponseRatingImproveAttribute(BaseModel):
    id: int
    name: str


class GetProductRatingBySkuResponseRatingGroup(BaseModel):
    conditions: list[GetProductRatingBySkuResponseRatingCondition]                  # Список условий, увеличивающих контент-рейтинг товара.
    improve_at_least: int                                                           # Количество атрибутов, которые нужно заполнить для получения 
                                                                                    # максимального балла в этой группе характеристик.
    improve_attributes: list[GetProductRatingBySkuResponseRatingImproveAttribute]   # Cписок атрибутов, заполнение которых может увеличить контент-рейтинг товара
    key: str                                                                        # Идентификатор группы
    name: str                                                                       # Название группы
    rating: float                                                                   # Рейтинг в группе
    weight: float                                                                   # Процент влияния характеристик группы на контент-рейтинг
    


class GetProductRatingBySkuResponseProductRating(BaseModel):
    sku: int
    rating: float
    groups: list[GetProductRatingBySkuResponseRatingGroup]


class PostProductRatingBySKU(BaseModel):
    products: Union[str, list[GetProductRatingBySkuResponseProductRating]]


# -------------------------------------------------------------------------------------------------------
class productsv1GetProductInfoStocksByWarehouseFbsResponseResult(BaseModel):
    fbs_sku: int
    present: int
    product_id: int
    reserved: int
    warehouse_id: int
    warehouse_name: str
    
class PostProductInfoStocksByWarehouseFBS(BaseModel):
    result: list[productsv1GetProductInfoStocksByWarehouseFbsResponseResult]
    


# -------------------------------------------------------------------------------------------------------
class productv2GetProductInfoStocksResponseItem(BaseModel):

    class productv2GetProductInfoStocksResponseStock(BaseModel):

        present : int
        reserved : int
        type : str
        
    offer_id : str
    product_id : int
    stocks : list[productv2GetProductInfoStocksResponseStock]

class PostProductInfoStocksList(BaseModel):

    items : list[productv2GetProductInfoStocksResponseItem]
    total : int
    
# -------------------------------------------------------------------------------------------------------
class productGetProductInfoPricesV4ResponseItem(BaseModel):

    class ItemCommissions(BaseModel):

        fbo_deliv_to_customer_amount : float                    #Последняя миля FBO
        fbo_direct_flow_trans_max_amount : float                #Магистраль до (FBO).
        fbo_direct_flow_trans_min_amount : float                #Магистраль от (FBO).
        fbo_fulfillment_amount : float                          #Комиссия за сборку заказа (FBO).
        fbo_return_flow_amount : float                          #Комиссия за возврат и отмену (FBO).
        fbo_return_flow_trans_min_amount : float                #Минимальная комиссия за обратную логистику (FBO).
        fbo_return_flow_trans_max_amount : float                #Максимальная комиссия за обратную логистику (FBO).
        
        fbs_deliv_to_customer_amount : float                    #Последняя миля (FBS).
        fbs_direct_flow_trans_max_amount : float                #Магистраль до (FBS).
        fbs_direct_flow_trans_min_amount : float                #Магистраль от (FBS).
        fbs_first_mile_min_amount : float                       #Минимальная комиссия за обработку отправления (FBS).
        fbs_first_mile_max_amount : float                       #Максимальная комиссия за обработку отправления (FBS).
        fbs_return_flow_amount : float                          #Комиссия за возврат и отмену, обработка отправления (FBS).
        fbs_return_flow_trans_max_amount : float                #Комиссия за возврат и отмену, магистраль до (FBS).
        fbs_return_flow_trans_min_amount : float                #Комиссия за возврат и отмену, магистраль от (FBS).
        sales_percent : float                                   #Процент комиссии за продажу (FBO и FBS).

    class ItemPrice(BaseModel):

        marketing_price : str
        marketing_seller_price : str
        min_ozon_price : str
        old_price : str
        premium_price : str
        price : str
        recommended_price : str
        retail_price : str
        vat : str

    class ItemMarketingActions(BaseModel):

        class MarketingActionsMarketingAction(BaseModel):
            
            date_from : datetime
            date_to : datetime
            discount_value : str
            title : str

        actions : list[MarketingActionsMarketingAction]
        current_period_from : Optional[datetime]
        current_period_to : Optional[datetime]
        ozon_actions_exist : bool


    commissions : ItemCommissions
    marketing_actions : Optional[ItemMarketingActions]
    offer_id : str
    price : ItemPrice
    price_index : str
    product_id : int
    volume_weight : float

class productGetProductInfoPricesV4ResponseResult(BaseModel):
    items : list[productGetProductInfoPricesV4ResponseItem]
    last_id : str
    total : int


class PostProductInfoPricesList(BaseModel):
    result : productGetProductInfoPricesV4ResponseResult

# -------------------------------------------------------------------------------------------------------
class v1GetProductInfoDiscountedResponseItem(BaseModel):
    comment_reason_damaged: str                                                     # Комментарий к причине повреждения.
    condition: str                                                                  # Состояние товара — новый или Б/У.
    condition_estimation: str                                                       # Состояние товара по шкале от 1 до 7:
                                                                                        # 1 — удовлетворительное,
                                                                                        # 2 — хорошее,
                                                                                        # 3 — очень хорошее,
                                                                                        # 4 — отличное,
                                                                                        # 5–7 — как новый.
    defects: str                                                                    # Дефекты товара.
    discounted_sku: int                                                             # SKU уценённого товара.
    mechanical_damage: str                                                          # Описание механического повреждения.
    package_damage: str                                                             # Описание повреждения упаковки.
    packaging_violation: str                                                        # Признак нарушения целостности упаковки.
    reason_damaged: str                                                             # Причина повреждения.
    repair: str                                                                     # Признак, что товар отремонтирован.
    shortage: str                                                                   # Признак, что товар некомплектный.
    sku: int                                                                        # SKU основного товара.
    warranty_type: str                                                              # Наличие у товара действующей гарантии.


class PostProductInfoDiscounted(BaseModel):
    items: list[v1GetProductInfoDiscountedResponseItem]

# -------------------------------------------------------------------------------------------------------

class GetActionsList(BaseModel):

    id : int
    title : str
    action_type : str
    description : str
    date_start : datetime
    date_end : datetime
    freeze_date : str
    potential_products_count : int
    participating_products_count : int
    is_participating : bool
    banned_products_count : int
    with_targeting : bool
    order_amount : int
    discount_type : str
    discount_value : int

# -------------------------------------------------------------------------------------------------------

class PostActionsCandidates(BaseModel):
    class seller_apiProduct(BaseModel):
        id : int
        price : int
        action_price : float
        max_action_price : float
        add_mode : str
        min_stock : int
        stock : int

    products : list[seller_apiProduct]
    total : int

# -------------------------------------------------------------------------------------------------------
class WarehouseFirstMileTypeEnum(str, Enum):
    DropOff = 'DropOff'
    PickUp = 'PickUp'


class WarehouseFirstMileType(BaseModel):
    dropoff_point_id : str
    dropoff_timeslot_id : int
    first_mile_is_changing : bool
    first_mile_type : Union[WarehouseFirstMileTypeEnum, str]

class WarehouseListResponseWarehouse(BaseModel):
    warehouse_id : int
    name : str
    is_rfbs : bool
    first_mile_type : Optional[WarehouseFirstMileType]
    is_able_to_set_price : bool
    has_entrusted_acceptance : bool
    can_print_act_in_advance : bool
    has_postings_limit : bool
    is_karantin : bool                          #Признак, что склад не работает из-за карантина.
    is_kgt : bool
    is_timetable_editable : bool
    min_postings_limit : int
    postings_limit : int
    min_working_days : int
    working_days : list[int]


class PostWarehouseList(BaseModel):
    result : list[WarehouseListResponseWarehouse]

# -------------------------------------------------------------------------------------------------------

class DeliveryMethodListResponseDeliveryMethod(BaseModel):
    company_id : int
    created_at : datetime
    cutoff : str
    id : int
    name : str
    provider_id : int
    status : str
    template_id : int
    updated_at : datetime
    warehouse_id : int


class PostDeliveryMethodList(BaseModel):
    has_next : bool
    result : list[DeliveryMethodListResponseDeliveryMethod]

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

class GetSupplyOrdersListResponseSupplyOrder(BaseModel):
    class v1Timeslot(BaseModel):
        from_: str
        to: str

        class Config:
            fields = {'from_': 'from'}

    class v1Warehouse(BaseModel):
        address: str
        name: str
        warehouse_id: int

    created_at: str
    local_timeslot: Optional[v1Timeslot]                                            # Интервал поставки по местному времени
    preferred_supply_date_from: str                                                 # Дата, с которой вы хотите привезти поставку на склад. Только для заявок с вРЦ.
    preferred_supply_date_to: str                                                   # Дата, до которой вы хотите привезти поставку на склад. Только для заявок с вРЦ.
    state: str                                                                      # Статус поставки по заявке:
                                                                                        # DRAFT — черновик заявки. Только для заявок с вРЦ.
                                                                                        # SUPPLY_VARIANTS_ARRANGING — подбор вариантов отгрузки. Только для заявок с вРЦ.
                                                                                        # HAS_NO_SUPPLY_VARIANTS_ARCHIVE — нет вариантов отгрузки. Заявка в архиве.
                                                                                        # HAS_NO_SUPPLY_VARIANTS_NEW — нет вариантов отгрузки.
                                                                                        # SUPPLY_VARIANT_CONFIRMATION — согласование отгрузки. Только для заявок с вРЦ.
                                                                                        # TIMESLOT_BOOKING — бронирование времени.
                                                                                        # DATA_FILLING — заполнение данных.
                                                                                        # READY_TO_SUPPLY — готова к отгрузке.
                                                                                        # ACCEPTED_AT_SUPPLY_WAREHOUSE — принята на точке отгрузки.
                                                                                        # IN_TRANSIT — в пути.
                                                                                        # ACCEPTANCE_AT_STORAGE_WAREHOUSE — приёмка на складе.
                                                                                        # REPORTS_CONFIRMATION_AWAITING — согласование актов.
                                                                                        # REPORT_REJECTED — спор.
                                                                                        # COMPLETED — завершена.
                                                                                        # REJECTED_AT_SUPPLY_WAREHOUSE — отказано в приёмке.
                                                                                        # CANCELLED — отменена.
                                                                                        # OVERDUE — просрочена.
    supply_order_id: int                                                            # Идентификатор заявки на поставку.    
    supply_order_number: str                                                        # Номер заявки.
    supply_warehouse: Optional[v1Warehouse]                                         # Склад поставки.
    time_left_to_prepare_supply: int                                                # Время в секундах, оставшееся на заполнение данных по поставке. Только для заявок с вРЦ.
    time_left_to_select_supply_variant: int                                         # Время в секундах, оставшееся на выбор варианта отгрузки. Только для заявок с вРЦ.
    total_items_count: int                                                          # Общее количество товаров в заявке.
    total_quantity: int                                                             # Общее количество единиц товара в заявке.


class PostSupplyOrderListResponse(BaseModel):
    has_next: bool
    supply_orders: list[GetSupplyOrdersListResponseSupplyOrder]
    total_supply_orders_count: int


class GetSupplyOrderItemsResponseItem(BaseModel):
    icon_path: str                                                                  # Ссылка на изображение товара.
    name: str                                                                       # Название товара.
    offer_id: str                                                                   # Артикул товара.
    quantity: int                                                                   # Количество товара.
    sku: int                                                                        # Идентификатор товара в системе Ozon — SKU.


class PostSupplyOrderItemsResponse(BaseModel):
    has_next: bool
    items: list[GetSupplyOrderItemsResponseItem]
    total_items_count: int


# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
class v2FboPosting(BaseModel):
    class v2AdditionalDataItem(BaseModel):
        key : str
        value : str

    class FboPostingFboPostingAnalyticsData(BaseModel):
        city : str
        delivery_type : str
        is_legal : bool
        is_premium : bool
        payment_type_group_name : str
        region : str
        warehouse_id : int
        warehouse_name : str

    class v2PostingFinancialData(BaseModel):
        class PostingFinancialDataServices(BaseModel):
            marketplace_service_item_deliv_to_customer : float
            marketplace_service_item_direct_flow_trans : float
            marketplace_service_item_dropoff_ff : float
            marketplace_service_item_dropoff_pvz : float
            marketplace_service_item_dropoff_sc : float
            marketplace_service_item_fulfillment : float
            marketplace_service_item_pickup : float
            marketplace_service_item_return_after_deliv_to_customer : float
            marketplace_service_item_return_flow_trans : float
            marketplace_service_item_return_not_deliv_to_customer : float
            marketplace_service_item_return_part_goods_customer : float

        class PostingFinancialDataProduct(BaseModel):
            class PostingFinancialDataServices(BaseModel):
                marketplace_service_item_deliv_to_customer : float
                marketplace_service_item_direct_flow_trans : float
                marketplace_service_item_dropoff_ff : float
                marketplace_service_item_dropoff_pvz : float
                marketplace_service_item_dropoff_sc : float
                marketplace_service_item_fulfillment : float
                marketplace_service_item_pickup : float
                marketplace_service_item_return_after_deliv_to_customer : float	
                marketplace_service_item_return_flow_trans : float	
                marketplace_service_item_return_not_deliv_to_customer : float	
                marketplace_service_item_return_part_goods_customer : float	
            
            class ProductPicking(BaseModel):
                amount : float
                moment : datetime
                tag : str
            
            actions : list[str]
            client_price : str
            commission_amount : float
            commission_percent : int
            item_services : PostingFinancialDataServices
            old_price : float
            payout : float
            picking : Optional[ProductPicking]
            price : float
            product_id : int
            quantity : int
            total_discount_percent : float
            total_discount_value : float


        posting_services : Optional[PostingFinancialDataServices]                   # FIXME: optional?
        products : list[PostingFinancialDataProduct]

    class v2PostingProduct(BaseModel):
        digital_code : Optional[list[str]]
        name : str
        offer_id : str
        price : str
        quantity : int
        sku : int


    additional_data : list[v2AdditionalDataItem]
    analytics_data : FboPostingFboPostingAnalyticsData
    cancel_reason_id : int
    created_at : datetime
    financial_data : v2PostingFinancialData
    in_process_at : datetime
    order_id : int
    order_number : str
    posting_number : str
    products : list[v2PostingProduct]
    status : str


class PostPostingFboList(BaseModel):
    result : list[v2FboPosting]


# -------------------------------------------------------------------------------------------------------
class TplIntegrationEnum(str, Enum):
    ozon = 'ozon'                       #доставка службой Ozon.
    tpl_tracking = 'tpl_tracking'       #доставка интегрированной службой.
    non_integrated = 'non_integrated'   #доставка сторонней службой.
    aggregator = 'aggregator'           #доставка через партнёрскую доставку Ozon.
    hybrid = 'hybrid'

class FbsPostingStatusEnum(str, Enum):
    """This enum is crucial for conveying postings into Moysklad"""
    awaiting_registration = 'awaiting_registration'                 # ожидает регистрации
    acceptance_in_progress = 'acceptance_in_progress'               # идёт приёмка
    awaiting_approve = 'awaiting_approve'                           # ожидает подтверждения
    awaiting_packaging = 'awaiting_packaging'                       # ожидает упаковки
    awaiting_deliver = 'awaiting_deliver'                           # ожидает отгрузки
    arbitration = 'arbitration'                                     # арбитраж
    client_arbitration = 'client_arbitration'                       # клиентский арбитраж доставки
    delivering = 'delivering'                                       # доставляется
    driver_pickup = 'driver_pickup'                                 # у водителя
    delivered = 'delivered'                                         # доставлено
    cancelled = 'cancelled'                                         # отменено
    not_accepted = 'not_accepted'                                   # не принят на сортировочном центре
    sent_by_seller = 'sent_by_seller'                               # отправлено продавцом

class v3FbsPosting(BaseModel):
    class v3Addressee(BaseModel):
        name : str
        phone : str

    class v3FbsPostingAnalyticsData(BaseModel):
        city : str
        delivery_date_begin : Optional[datetime]
        delivery_date_end : Optional[datetime]
        delivery_type : str
        is_legal : bool
        is_premium : bool
        payment_type_group_name : str
        region : str
        tpl_provider : str
        tpl_provider_id : int
        warehouse : str
        warehouse_id : int

    class v3Barcodes(BaseModel):
        lower_barcode : str
        upper_barcode : str

    class v3Cancellation(BaseModel):
        affect_cancellation_rating : bool
        cancel_reason : Optional[str]
        cancel_reason_id : int
        cancellation_initiator : Optional[str]
        cancellation_type : Optional[str]
        cancelled_after_ship : bool

    class v3Customer(BaseModel):                    # TODO : not finished yet!
        # address : v3Address
        customer_email : str
        customer_id : int


    class v3DeliveryMethod(BaseModel):
        id : int
        name : str
        tpl_provider : str
        tpl_provider_id : int
        warehouse : str
        warehouse_id : int

    class v3PostingFinancialData(BaseModel):
        class PostingFinancialDataServices(BaseModel):
            marketplace_service_item_deliv_to_customer : float
            marketplace_service_item_direct_flow_trans : float
            marketplace_service_item_dropoff_ff : float
            marketplace_service_item_dropoff_pvz : float
            marketplace_service_item_dropoff_sc : float
            marketplace_service_item_fulfillment : float
            marketplace_service_item_pickup : float
            marketplace_service_item_return_after_deliv_to_customer : float
            marketplace_service_item_return_flow_trans : float
            marketplace_service_item_return_not_deliv_to_customer : float
            marketplace_service_item_return_part_goods_customer : float

        class PostingFinancialDataProduct(BaseModel):
            class PostingFinancialDataServices(BaseModel):
                marketplace_service_item_deliv_to_customer : float
                marketplace_service_item_direct_flow_trans : float
                marketplace_service_item_dropoff_ff : float
                marketplace_service_item_dropoff_pvz : float
                marketplace_service_item_dropoff_sc : float
                marketplace_service_item_fulfillment : float
                marketplace_service_item_pickup : float
                marketplace_service_item_return_after_deliv_to_customer : float	
                marketplace_service_item_return_flow_trans : float	
                marketplace_service_item_return_not_deliv_to_customer : float	
                marketplace_service_item_return_part_goods_customer : float	
            
            class ProductPicking(BaseModel):
                amount : float
                moment : datetime
                tag : str
            
            actions : list[str]
            client_price : str
            commission_amount : float
            commission_percent : int
            item_services : PostingFinancialDataServices
            old_price : float
            payout : float
            picking : Optional[ProductPicking]
            price : float
            product_id : int
            quantity : int
            total_discount_percent : float
            total_discount_value : float


        posting_services : PostingFinancialDataServices
        products : list[PostingFinancialDataProduct]

    class v3FbsPostingProduct(BaseModel):
        mandatory_mark : list[str]
        name : str
        offer_id : str
        price : str
        quantity : int
        sku : int

    class v3FbsPostingRequirementsV3(BaseModel):
        products_requiring_gtd : list[int]
        products_requiring_country : list[int]

    addressee : Optional[v3Addressee]
    analytics_data : Optional[v3FbsPostingAnalyticsData]        # optional when the order is cancelled before getting processed
    barcodes : Optional[v3Barcodes]
    cancellation : v3Cancellation
    customer : Optional[v3Customer]                          #v3Customer
    delivering_date : Optional[datetime]
    delivery_method : v3DeliveryMethod
    financial_data : v3PostingFinancialData
    in_process_at : datetime
    is_express : bool
    order_id : int
    order_number : str
    posting_number : str
    products : list[v3FbsPostingProduct]
    requirements : v3FbsPostingRequirementsV3
    shipment_date : datetime
    status : FbsPostingStatusEnum                           # FIXME : here was str as a validation unit, changed as an experiment 
    tpl_integration_type : TplIntegrationEnum
    tracking_number : str


class v3GetFbsPostingListResponseV3Result(BaseModel):
    has_next : bool
    postings : list[v3FbsPosting]


class PostPostingFbsList(BaseModel):
    result : v3GetFbsPostingListResponseV3Result


# -------------------------------------------------------------------------------------------------------
class commonReturnsCompanyItemFbo(BaseModel):
    accepted_from_customer_moment : datetime
    company_id : int
    current_place_name : str
    dst_place_name : str
    id : int
    is_opened : bool
    posting_number : str
    return_reason_name : str
    returned_to_ozon_moment : Optional[datetime]
    sku : int
    status_name : str


class PostReturnsFBO(BaseModel):
    returns : list[commonReturnsCompanyItemFbo]
    last_id : int


# -------------------------------------------------------------------------------------------------------
class FbsReturnStatusEnum(str, Enum):
    returned_to_seller = 'returned_to_seller'                       #возвращён продавцу.
    waiting_for_seller = 'waiting_for_seller'                       #в ожидании продавца.
    accepted_from_customer = 'accepted_from_customer'               #принят от покупателя.
    cancelled_with_compensation = 'cancelled_with_compensation'     #отменено с компенсацией.
    ready_for_shipment = 'ready_for_shipment'                       #готов к отправке.
    disposed = 'disposed'                                           #утилизирован.
    disposing = 'disposing'                                         #утилизируется.
    deleted = 'deleted'                                             #удален.
    moving = 'moving'                                               #в движении.
    arrived_for_resale = 'arrived_for_resale'                       # ko
    

class commonReturnsCompanyItemFbs(BaseModel):
    """Информация о возврате"""
    accepted_from_customer_moment : Optional[datetime]
    clearing_id : int
    commission : float
    commission_percent : float
    id : int
    is_moving : bool
    is_opened : bool
    last_free_waiting_day : Optional[str]
    place_id : int
    moving_to_place_name : str
    picking_amount : Optional[float]
    posting_number : str
    picking_tag: Optional[str]
    price : float
    price_without_commission : float
    product_id : int
    product_name : str
    quantity : int
    return_clearing_id: Optional[int]
    return_date : Optional[str]
    return_reason_name : str
    waiting_for_seller_date_time : Optional[str]
    returned_to_seller_date_time : Optional[str]
    waiting_for_seller_days : int
    returns_keeping_cost : float
    sku : int
    status : FbsReturnStatusEnum


class PostReturnsFBS(BaseModel):
    """Позволяет получить информацию о возвращённых товарах, которые продаются со склада продавца."""
    returns : list[commonReturnsCompanyItemFbs]
    last_id : int


class PostReturnsFBSResult(BaseModel):
    """Позволяет получить информацию о возвращённых товарах, которые продаются со склада продавца."""
    result : PostReturnsFBS


# -------------------------------------------------------------------------------------------------------
class FinancialOperationTypeEnum(str, Enum):
    ClientReturnAgentOperation = 'ClientReturnAgentOperation'                                                       #получение возврата, отмены, невыкупа от покупателя,
    MarketplaceMarketingActionCostOperation = 'MarketplaceMarketingActionCostOperation'                             #услуги продвижения товаров,
    MarketplaceSaleReviewsOperation = 'MarketplaceSaleReviewsOperation'                                             #приобретение отзывов на платформе,
    MarketplaceSellerCompensationOperation = 'MarketplaceSellerCompensationOperation'                               #прочие компенсации,
    OperationAgentDeliveredToCustomer = 'OperationAgentDeliveredToCustomer'                                         #доставка покупателю,
    OperationAgentDeliveredToCustomerCanceled = 'OperationAgentDeliveredToCustomerCanceled'                         #доставка покупателю — исправленное начисление,
    OperationAgentStornoDeliveredToCustomer = 'OperationAgentStornoDeliveredToCustomer'                             #доставка покупателю — отмена начисления,
    OperationClaim = 'OperationClaim'                                                                               #начисление по претензии,
    OperationCorrectionSeller = 'OperationCorrectionSeller'                                                         #инвентаризация взаиморасчетов,
    OperationDefectiveWriteOff = 'OperationDefectiveWriteOff'                                                       #компенсация за повреждённый на складе товар,
    OperationItemReturn = 'OperationItemReturn'                                                                     #доставка и обработка возврата, отмены, невыкупа,
    OperationLackWriteOff = 'OperationLackWriteOff'                                                                 #компенсация за утерянный на складе товар,
    OperationMarketplaceCrossDockServiceWriteOff = 'OperationMarketplaceCrossDockServiceWriteOff'                   #доставка товаров на склад Ozon (кросс-докинг),
    OperationMarketplaceServiceStorage = 'OperationMarketplaceServiceStorage'                                       #услуга размещения товаров на складе,
    OperationSetOff = 'OperationSetOff'                                                                             #взаимозачёт с другими договорами контрагента,
    MarketplaceSellerReexposureDeliveryReturnOperation = 'MarketplaceSellerReexposureDeliveryReturnOperation'       #перечисление за доставку от покупателя,
    OperationReturnGoodsFBSofRMS = 'OperationReturnGoodsFBSofRMS'                                                   #доставка и обработка возврата, отмены, невыкупа,
    ReturnAgentOperationRFBS = 'ReturnAgentOperationRFBS'                                                           #возврат перечисления за доставку покупателю,
    MarketplaceSellerShippingCompensationReturnOperation = 'MarketplaceSellerShippingCompensationReturnOperation'   #компенсация перечисления за доставку,
    OperationMarketplaceServicePremiumCashback = 'OperationMarketplaceServicePremiumCashback'                       #услуга продвижения Premium.


class FinancialTransactionTypeEnum(str, Enum):
    all = 'all'                                     #все
    orders = 'orders'                               #заказы
    returns = 'returns'                             #возвраты
    services = 'services'                           #сервисные сборы
    compensation = 'compensation'                   #компенсация
    transferDelivery = 'transferDelivery'           #стоимость доставки
    transfer_delivery = 'transfer_delivery'           #стоимость доставки
    other = 'other'                                 #прочее


class FinancialServiceEnum(str, Enum):
    MarketplaceNotDeliveredCostItem = 'MarketplaceNotDeliveredCostItem'                                     # возврат невостребованного товара от покупателя на склад.
    MarketplaceReturnAfterDeliveryCostItem = 'MarketplaceReturnAfterDeliveryCostItem'                       # возврат от покупателя на склад после доставки.
    MarketplaceDeliveryCostItem = 'MarketplaceDeliveryCostItem'                                             # доставка товара до покупателя.
    MarketplaceSaleReviewsItem = 'MarketplaceSaleReviewsItem'                                               # приобретение отзывов на платформе.
    ItemAdvertisementForSupplierLogistic = 'ItemAdvertisementForSupplierLogistic'                           # доставка товаров на склад Ozon — кросс-докинг.
    ItemAdvertisementForSupplierLogisticSeller = 'ItemAdvertisementForSupplierLogisticSeller'               # транспортно-экспедиционные услуги.
    MarketplaceServiceStorageItem = 'MarketplaceServiceStorageItem'                                         # размещения товаров.
    MarketplaceMarketingActionCostItem = 'MarketplaceMarketingActionCostItem'                               # продвижение товаров.
    MarketplaceServiceItemInstallment = 'MarketplaceServiceItemInstallment'                                 # продвижению и продажа в рассрочку.
    MarketplaceServiceItemMarkingItems = 'MarketplaceServiceItemMarkingItems'                               # обязательная маркировка товаров.
    MarketplaceServiceItemFlexiblePaymentSchedule = 'MarketplaceServiceItemFlexiblePaymentSchedule'         # гибкий график выплат.
    MarketplaceServiceItemReturnFromStock = 'MarketplaceServiceItemReturnFromStock'                         # комплектация товаров для вывоза продавцом.
    MarketplaceServiceItemDelivToCustomer = 'MarketplaceServiceItemDelivToCustomer'                         # последняя миля.
    MarketplaceServiceItemDirectFlowTrans = 'MarketplaceServiceItemDirectFlowTrans'                         # магистраль.
    MarketplaceServiceItemDropoffFF = 'MarketplaceServiceItemDropoffFF'                                     # обработка отправления.
    MarketplaceServiceItemDropoffPVZ = 'MarketplaceServiceItemDropoffPVZ'                                   # обработка отправления.
    MarketplaceServiceItemDropoffSC = 'MarketplaceServiceItemDropoffSC'                                     # обработка отправления.
    MarketplaceServiceItemFulfillment = 'MarketplaceServiceItemFulfillment'                                 # сборка заказа.
    MarketplaceServiceItemPickup = 'MarketplaceServiceItemPickup'                                           # выезд транспортного средства по адресу продавца для забора отправлений — Pick-up.
    MarketplaceServiceItemReturnAfterDelivToCustomer = 'MarketplaceServiceItemReturnAfterDelivToCustomer'   # обработка возврата.
    MarketplaceServiceItemReturnFlowTrans = 'MarketplaceServiceItemReturnFlowTrans'                         # обратная магистраль.
    MarketplaceServiceItemReturnNotDelivToCustomer = 'MarketplaceServiceItemReturnNotDelivToCustomer'       # обработка отмен.
    MarketplaceServiceItemReturnPartGoodsCustomer = 'MarketplaceServiceItemReturnPartGoodsCustomer'         # обработка невыкупа.
    MarketplaceServiceDCFlowTrans = 'MarketplaceServiceDCFlowTrans'                                         # TODO: пока непонятно из документаци.
    MarketplaceServiceDeliveryGoodsToCustAgregator = 'MarketplaceServiceDeliveryGoodsToCustAgregator'       # TODO: пока непонятно из документаци.
    MarketplaceServiceReturnUnclaimedGoodsAgregator = 'MarketplaceServiceReturnUnclaimedGoodsAgregator'     # TODO: пока непонятно из документаци.
    MarketplaceServiceItemReturnFlowLogistic = 'MarketplaceServiceItemReturnFlowLogistic'                   # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDirectFlowLogistic = 'MarketplaceServiceItemDirectFlowLogistic'                   # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDropoffPPZ = 'MarketplaceServiceItemDropoffPPZ'                                   # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDirectFlowLogisticDC = 'MarketplaceServiceItemDirectFlowLogisticDC'               # TODO: пока непонятно из документаци.
    MarketplaceSellerCostOperation = 'MarketplaceSellerCostOperation'                                       # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDeliveryKGT = 'MarketplaceServiceItemDeliveryKGT'                                 # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDirectFlowLogisticVDC = 'MarketplaceServiceItemDirectFlowLogisticVDC'             # TODO: пока непонятно из документаци.
    MarketplaceServiceItemDropoffTSC = 'MarketplaceServiceItemDropoffTSC'                                   # TODO: пока непонятно из документаци.
    MarketplaceServiceItemReturnKGT = 'MarketplaceServiceItemReturnKGT'                                     # TODO: пока непонятно из документаци.
    MarketplaceServicePremiumCashback = 'MarketplaceServicePremiumCashback'                                 # TODO: пока непонятно из документаци.
    MarketplaceServicePremiumCashbackIndividualPoints = 'MarketplaceServicePremiumCashbackIndividualPoints' # TODO: пока непонятно из документаци.
    OperationCorrectionSeller = 'OperationCorrectionSeller'                                                 # TODO: пока непонятно из документаци. 
    MarketplaceServicePremiumPromotion = 'MarketplaceServicePremiumPromotion'                               # TODO: пока непонятно из документаци. 
    MarketplaceReturnStorageServiceAtThePickupPointFbsItem = 'MarketplaceReturnStorageServiceAtThePickupPointFbsItem'   # TODO: пока непонятно из документаци.
    MarketplaceReturnStorageServiceInTheWarehouseFbsItem = 'MarketplaceReturnStorageServiceInTheWarehouseFbsItem' # TODO: пока непонятно из документаци.
    OperationMarketplaceWithHoldingForUndeliverableGoods = 'OperationMarketplaceWithHoldingForUndeliverableGoods' # TODO: пока непонятно из документаци.
    MarketplaceRedistributionOfAcquiringOperation = 'MarketplaceRedistributionOfAcquiringOperation' # TODO: пока непонятно из документаци.
    MarketplaceReturnDisposalServiceFbsItem = 'MarketplaceReturnDisposalServiceFbsItem'
    MarketplaceServiceBrandCommission = 'MarketplaceServiceBrandCommission'                                 # TODO: 
    MarketplaceServiceItemRedistributionReturnsPVZ = 'MarketplaceServiceItemRedistributionReturnsPVZ'       # TODO:


class FinancialDeliverySchemaEnum(str, Enum):
    FBO = "FBO"
    FBS = "FBS"
    RFBS = "RFBS"
    Crossborder = "Crossborder"


class FinanceTransactionListV3ResponseOperation(BaseModel):
    """Информация об операциях."""
    class OperationItem(BaseModel):
        """Информация о товаре."""
        name : str
        sku : int

    class OperationPosting(BaseModel):
        """Информация об отправлении."""
        delivery_schema : Union[FinancialDeliverySchemaEnum, str]
        order_date : Optional[str]
        posting_number : Optional[str]
        warehouse_id : int

    class OperationService(BaseModel):
        """"Дополнительные услуги."""
        name : FinancialServiceEnum
        price : float


    accruals_for_sale : float           #Стоимость товаров с учётом скидок продавца.
    amount : float                      #Итоговая сумма операции.
    delivery_charge : float             #Стоимость доставки для начислений по тарифам, которые действовали до 1 февраля 2021 года, а также начислений для крупногабаритных товаров.
    items : list[OperationItem]         #Информация о товаре.
    operation_date : str                #Дата операции.
    operation_id : int                  #Идентификатор операции.
    operation_type : str                #Тип операции.
    operation_type_name : str           #Название типа операции.
    posting : OperationPosting          #Информация об отправлении.
    return_delivery_charge : float      #Плата за возвраты и отмены для начислений по тарифам, которые действовали до 1 февраля 2021 года, а также начислений для крупногабаритных товаров.
    sale_commission : float             #Комиссия за продажу или возврат комиссии за продажу.
    services : Optional[list[OperationService]]   #Дополнительные услуги.
    type : str                          #Тип начисления


class PostFinanceTransactionList(BaseModel):
    """Возвращает подробную информацию по всем начислениям. Максимальный период, за который можно получить информацию в одном запросе — 3 месяца."""
    operations : list[FinanceTransactionListV3ResponseOperation]
    page_count : int
    row_count : int


class PostFinanceTransactionListResult(BaseModel):
    """Возвращает подробную информацию по всем начислениям. Максимальный период, за который можно получить информацию в одном запросе — 3 месяца."""
    result : PostFinanceTransactionList


# -------------------------------------------------------------------------------------------------------
class AnalyticsItemTurnoverDataV3ResponseItemTurnover(BaseModel):
    """Данные по товарам категории."""
    avg_sold_items : float                                  #Среднесуточные продажи за определённый период. Указывается в штуках.
    avg_sold_litres : float                                 #Среднесуточные продажи за определённый период. Измеряется в литрах.
    avg_stock_items : float                                 #Среднесуточный объём товара на складе в литрах.
    avg_stock_items_free : float                            #Сколько единиц товара можно размещать на складе бесплатно. Рассчитывается по формуле: Среднесуточные продажи товара (л/дн) × Пороговая оборачиваемость (дн) ÷ Объём (л).
    avg_stock_litres : float                                #Среднесуточный остаток на складах Ozon в литрах.
    discounted : bool                                       #Уценённый товар.
    height : float                                          #Высота товара.
    item_commission_part : float                            #Часть от стоимости размещения категории в рублях.
    length : float                                          #Длина товара.
    min_daily_sales : float                                 #Сколько нужно продавать в день, чтобы размещение товара было бесплатным. Рассчитывается по формуле: Среднесуточный остаток товара (л) ÷ Пороговая оборачиваемость (дн) ÷ Объем (л).
    name : str                                              #Название товара.
    offer_id : str                                          #Артикул.
    recommendation : str                                    #Рекомендация, что нужно сделать с товаром по данным об оборачиваемости этого товара.
    sku : int                                               #Идентификатор товара в системе Ozon — SKU.
    stock_items_total : int                                 #Доступно к продаже всего в штуках.
    threshold_free : int                                    #Пороговая оборачиваемость в днях.
    turnover : str                                          #Фактическая оборачиваемость в днях.
    volume : float                                          #Объём товара.
    width : float                                           #Ширина товара.


class AnalyticsItemTurnoverDataV3ResponseCategory(BaseModel):
    """Данные по категориям."""
    avg_sold_litres : float                                                             #Среднесуточные продажи за определённый период. Измеряется в литрах.
    avg_stock_litres : float                                                            #Среднесуточный остаток на складах Ozon в литрах.
    billed_days : int                                                                   #Количество прошедших дней с платным размещением.
    category_id : int                                                                   #Идентификатор категории.
    commission : float                                                                  #Стоимость размещения одного литра товара в рублях.
    fee : float                                                                         #Тариф за размещение в рублях. Зависит от объёма и количества дней размещения.
    threshold_free : int                                                                #Пороговая оборачиваемость для бесплатного размещения. Измеряется в днях.
    threshold_used : int                                                                #Превышенный порог оборачиваемости, по которому определили тариф. Измеряется в днях.
    turnover : str                                                                      #Фактическая оборачиваемость в днях.
    turnover_items : list[AnalyticsItemTurnoverDataV3ResponseItemTurnover]              #Данные по товарам категории.


class PostAnalyticsItemTurnover(BaseModel):
    """Метод для получения отчёта по оборачиваемости (FBO) по категориям за последние 15 дней."""
    categories : list[AnalyticsItemTurnoverDataV3ResponseCategory]
    commission_total : float
    date : str
    period : str
# -------------------------------------------------------------------------------------------------------


class analyticsDataRowDimension(BaseModel):
    """Группировка данных в отчёте."""
    id : str
    name : str


class analyticsDataRow(BaseModel):
    """Массив данных."""
    dimensions : list[analyticsDataRowDimension]
    metrics : list[float]


class AnalyticsGetDataResponseResult(BaseModel):
    """Результаты запроса."""
    data : list[analyticsDataRow]
    totals : list[float]


class PostAnalyticsData(BaseModel):
    """Уĸажите период и метриĸи, ĸоторые нужно посчитать — в ответе будет аналитиĸа, сгруппированная по параметру dimensions."""
    result : AnalyticsGetDataResponseResult
    timestamp : str


# -------------------------------------------------------------------------------------------------------
class analyticsStockOnWarehouseResultRows(BaseModel):
    sku: int
    item_code: str
    item_name: str
    free_to_sell_amount: int                                                                            # Количество товара, доступное к продаже на Ozon.
    promised_amount: int                                                                                # Количество товара, указанное в подтверждённых будущих поставках.
    reserved_amount: int                                                                                # Количество товара, зарезервированное для покупки, возврата и перевозки между складами.
    warehouse_name: str                                                                                 # Название склада, где находится товар.


class analyticsStockOnWarehouseResponseResult(BaseModel):
    rows: Optional[list[analyticsStockOnWarehouseResultRows]]


class Postv2AnalyticsStockOnWarehousesResponse(BaseModel):
    result: analyticsStockOnWarehouseResponseResult

# -------------------------------------------------------------------------------------------------------
class CampaignStateEnum(str, Enum):
    CAMPAIGN_STATE_RUNNING = 'CAMPAIGN_STATE_RUNNING'                                     #активная кампания
    CAMPAIGN_STATE_PLANNED = 'CAMPAIGN_STATE_PLANNED'                                     #кампания, сроки проведения которой ещё не наступили
    CAMPAIGN_STATE_STOPPED = 'CAMPAIGN_STATE_STOPPED'                                     #кампания, сроки проведения которой завершились
    CAMPAIGN_STATE_INACTIVE = 'CAMPAIGN_STATE_INACTIVE'                                   #кампания, остановленная владельцем
    CAMPAIGN_STATE_ARCHIVED = 'CAMPAIGN_STATE_ARCHIVED'                                   #архивная кампания
    CAMPAIGN_STATE_MODERATION_DRAFT = 'CAMPAIGN_STATE_MODERATION_DRAFT'                   #отредактированная кампания до отправки на модерацию
    CAMPAIGN_STATE_MODERATION_IN_PROGRESS = 'CAMPAIGN_STATE_MODERATION_IN_PROGRESS'       #кампания, отправленная на модерацию
    CAMPAIGN_STATE_MODERATION_FAILED = 'CAMPAIGN_STATE_MODERATION_FAILED'                 #кампания, непрошедшая модерацию
    CAMPAIGN_STATE_FINISHED = 'CAMPAIGN_STATE_FINISHED'                                   #кампания завершена, дата окончания в прошлом, такую кампанию нельзя изменить, можно только клонировать или создать новую


class AdvObjectTypeEnum(str, Enum):
    SKU = 'SKU'                                                                     #реклама товаров в спонсорских полках c размещением на карточках товаров, в поиске или категории
    BANNER = 'BANNER'                                                               #баннерная рекламная кампания
    SIS = 'SIS'                                                                     #реклама магазина
    BRAND_SHELF = 'BRAND_SHELF'                                                     #брендовая полка
    BOOSTING_SKU = 'BOOSTING_SKU'                                                   #повышение товаров в каталоге
    ACTION = 'ACTION'                                                               #рекламная кампания для акций продавца
    ACTION_CAS = 'ACTION_CAS'                                                       #рекламная кампания для акции
    SEARCH_PROMO = 'SEARCH_PROMO'                                                   #Продвижение в поиске
    EXTERNAL_GOOGLE = 'EXTERNAL_GOOGLE'                                             #Внешнее продвижение Google Ads
    VIDEO_BANNER = 'VIDEO_BANNER'                                                   #Видеореклама
    PROMO_PACKAGE_SERVICE = 'PROMO_PACKAGE_SERVICE'                                 #Баннер на главной странице
    PROMO_PACKAGE_SERVICE_MANUAL_BILLING = 'PROMO_PACKAGE_SERVICE_MANUAL_BILLING'
    PROMO_PACKAGE = 'PROMO_PACKAGE'                                                 #Проведение видеострима


class ProductCampaignPlacementEnum(str, Enum):
    PLACEMENT_INVALID = 'PLACEMENT_INVALID'                             #не определено
    PLACEMENT_PDP = 'PLACEMENT_PDP'                                     #карточка товара
    PLACEMENT_SEARCH_AND_CATEGORY = 'PLACEMENT_SEARCH_AND_CATEGORY'     #поиск и категории


class extcampaignCampaign(BaseModel):
    """Список кампаний."""
    id : str
    title : str
    state : CampaignStateEnum
    advObjectType : Optional[AdvObjectTypeEnum]
    fromDate : str
    toDate : str
    budget : str
    dailyBudget : str
    placement : Optional[list[Union[ProductCampaignPlacementEnum, int]]]
    createdAt : datetime
    updatedAt : datetime


class GetPerfCampaign(BaseModel):
    """Список рекламных кампаний"""
    list : list[extcampaignCampaign]
    total : str

# -------------------------------------------------------------------------------------------------------
class extcampaignCampaignObject(BaseModel):
    """Идентификатор рекламируемого объекта:
    SKU — для рекламы товаров в спонсорских полках и в каталоге;
    числовой идентификатор — для баннерных кампаний."""
    id : str


class GetPerfCampaignObjects(BaseModel):
    """Список идентификаторов рекламируемых объектов"""
    list : list[extcampaignCampaignObject]

# --------------------------------------------------------------------------------------------------------
class PostPerfStatistics(BaseModel):
    """Статистика по кампании"""
    UUID: UUID4
    vendor: bool


class PerfStatisticsRequestStateEnum(str, Enum):
    NOT_STARTED = 'NOT_STARTED'                 #запрос ожидает выполнения
    IN_PROGRESS = 'IN_PROGRESS'                 #запрос выполняется в данный момент
    ERROR = 'ERROR'                             #выполнение запроса завершилось ошибкой
    OK = 'OK'                                   #запрос успешно выполнен


class GetPerfStatisticsStatus(BaseModel):
    """Cтатус отчёта"""
    class extstatStatisticsRequest(BaseModel):
        """Структура исходного запроса, отправленного на сервер и соответствующего заданному уникальному идентификатору"""
        campaignId: Optional[str]
        campaigns: list[str]
        from_: Optional[datetime] = Field(alias='from')
        to: Optional[datetime]
        dateFrom: Optional[Union[datetime, str]]
        dateTo: Optional[Union[datetime, str]]
        groupBy: str = Field(default='NO_GROUP_BY')
        objects: Optional[list[int]]
        attributionDays: Optional[str]

    UUID: UUID4
    state: PerfStatisticsRequestStateEnum
    createdAt: datetime
    updatedAt: datetime
    request: extstatStatisticsRequest
    error: Optional[str]
    link: Optional[str]
    kind: str


class GetPerfStatisticsReport(BaseModel):
    """Получить отчёты"""
    contentType: str


# -------------------------------------------------------------------------------------------------------
class PerfSearchBidRelevanceEnum(str, Enum):
    relevant = 'relevant'                   # релевантно
    not_relevant = 'not_relevant'           # не релевантно
    not_started = 'not_started'             # FIXME: undocumented
    in_progress = 'in_progress'             # релевантность ещё не определена
    on_moderation = 'on_moderation'         # релевантность ещё не определена, необходима ручная модерация


class extcampaignSearchBid(BaseModel):
    """Список поисковых фраз со ставками и статусом релевантности."""
    bid: str                                        # Ставка за 1000 показов (CPM) или 1000 кликов (CPC). 
                                                    # Единица измерения — одна миллионная доля рубля, округляется до копеек
    phrase: str                                     # Поисковая фраза
    relevanceStatus: PerfSearchBidRelevanceEnum     # Статус релевантности — соответствия поисковой фразы рекламируемому товару


class extcampaignGetProductsResponseProduct(BaseModel):
    """Список товаров кампании"""
    sku: str                                # Идентификатор товара: Ozon ID, SKU.
    bid: str                                # Ставка за 1000 показов (CPM) или 1000 кликов (CPC). Единица измерения — одна миллионная доля рубля, округляется до копеек.
                                            # Актуально только для рекламных кампаний с размещением на страницах каталога и поиска.
    groupId: str                            # Идентификатор группы товаров, если товар добавлен в группу.
                                            # Актуально только для рекламных кампаний с размещением на страницах каталога и поиска.
    stopWords: list[str]                    # Список стоп-слов.
                                            # Актуально только для рекламных кампаний с размещением на страницах каталога и поиска.
    phrases: list[extcampaignSearchBid]     # Список поисковых фраз со ставками и статусом релевантности.
    auctionStatus: list[int]                # FIXME: not documented



class GetPerfCampaignProducts(BaseModel):
    """Список товаров кампании"""
    products : list[extcampaignGetProductsResponseProduct]


# -------------------------------------------------------------------------------------------------------
class ListSearchPromoProductsResponseHint(BaseModel):
    """Максимальная ставка."""
    campaignId: str
    organisationTitle: str


class ListSearchPromoProductsResponsePreviousBid(BaseModel):
    """Информация о предыдущем значении ставки"""
    bid: float                                                  # Предыдущее значение bid
    bidPrice: str                                               # Предыдущее значение bidPrice
    updatedAt: str                                              # Дата и время последнего изменения ставки


class ListSearchPromoProductsResponseViews(BaseModel):
    """ Информация о просмотрах"""
    previousWeek: str                                           # Количество просмотров товара за последние 7–14 дней
    thisWeek: str                                               # Количество просмотров товара за последние 7 дней


class extcampaignListSearchPromoProductsResponseProduct(BaseModel):
    """Список товаров"""
    bid: float                                                  # Ставка за 1000 показов (CPM) или 1000 кликов (CPC). Единица измерения — 
                                                                # одна миллионная доля рубля, округляется до копеек
    bidPrice: str                                               # Ставка за 1000 показов (CPM) или 1000 кликов (CPC) в рублях
    hint: Optional[ListSearchPromoProductsResponseHint]         # Максимальная ставка
    imageUrl: str
    previousBid: Optional[ListSearchPromoProductsResponsePreviousBid]     # Информация о предыдущем значении ставки
    previousVisibilityIndex: str                                # Предыдущее значение visibilityIndex
    price: str                                                  # Цена товара
    sku: str                                                    # SKU рекламируемого товара
    sourceSku: str                                              # Артикул продавца
    title: str                                                  # Название товара
    views: ListSearchPromoProductsResponseViews                 # Информация о просмотрах.
    visibilityIndex: str                                        # Индекс видимости



class PostPerfSearchPromoProducts(BaseModel):
    """Список товаров организации. Если организация продаёт товары, в ответе будет список всех товаров продавца. 
    Если организация другого типа, в ответе будет список всех товаров 1P организации, добавленных в заданную компанию"""
    products: list[extcampaignListSearchPromoProductsResponseProduct]
    total: str


class v1GetTreeResponseItem(BaseModel):
    # _id: int | None = None                                                   # user defined field
    _parent_id: int | None = None                                            # user defined field
    description_category_id: int | None = None
    category_name: str | None = None
    children: Optional[List['v1GetTreeResponseItem']]
    disabled: bool
    type_id: int | None = None
    type_name: str | None = None

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        dump_ = super().dict(*args, **kwargs)
        dump_.pop('children')
        return dump_


class PostDescriptionCategoryTreeResponse(BaseModel):
    result: Optional[List[v1GetTreeResponseItem]]

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        def flatten_category_tree(category_tree_result: dict[str, Any]) -> list[dict[str, Any]]:
            top_level_categories = []
            second_level_categories = []
            type_level_categories = []

            for top_level_category in category_tree_result.get('result'):
                top_level_category_dump = v1GetTreeResponseItem(**top_level_category).to_dict()
                top_level_categories.append(
                    top_level_category_dump
                )
                for top_level_child in top_level_category.get('children'):
                    top_level_child_dump = v1GetTreeResponseItem(**top_level_child).to_dict()
                    top_level_child_dump['_parent_id'] = top_level_category_dump.get('description_category_id')
                    second_level_categories.append(
                        top_level_child_dump
                    )
                    for type_level_child in top_level_child.get('children'):
                        type_level_child_dump = v1GetTreeResponseItem(**type_level_child).to_dict()
                        type_level_child_dump['_parent_id'] = top_level_child_dump.get('description_category_id')
                        type_level_categories.append(
                                type_level_child_dump
                            )
                        
            return list(chain(*(
                top_level_categories,
                second_level_categories,
                type_level_categories
            )))


        
        _dump = super().dict(*args, **kwargs)
        return flatten_category_tree(category_tree_result=_dump)