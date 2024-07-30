from enum import Enum


class ResponseStatusEnum(str, Enum):
    ERROR = "ERROR"
    OK = "OK"


class TimeUnitEnum(str, Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


class OfferAvailabilityStatusType(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELISTED = "DELISTED"


class ProcessingStateEnum(str, Enum):
    READY = "READY"
    IN_WORK = "IN_WORK"
    NEED_CONTENT = "NEED_CONTENT"
    NEED_INFO = "NEED_INFO"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    CONTENT_PROCESSING = "CONTENT_PROCESSING"
    OTHER = "OTHER"
    UPDATE_ERROR = "UPDATE_ERROR"
    CREATE_ERROR = "CREATE_ERROR"
    

class ProcessingStateNoteTypeEnum(str, Enum):
    ASSORTMENT = "ASSORTMENT"
    CANCELLED = "CANCELLED"
    CONFLICTING_INFORMATION = "CONFLICTING_INFORMATION"
    DEPARTMENT_FROZEN = "DEPARTMENT_FROZEN"
    INCORRECT_INFORMATION = "INCORRECT_INFORMATION"
    LEGAL_CONFLICT = "LEGAL_CONFLICT"
    NEED_CLASSIFICATION_INFORMATION = "NEED_CLASSIFICATION_INFORMATION"
    NEED_INFORMATION = "NEED_INFORMATION"
    NEED_PICTURES = "NEED_PICTURES"
    NEED_VENDOR = "NEED_VENDOR"
    NO_CATEGORY = "NO_CATEGORY"
    NO_KNOWLEDGE = "NO_KNOWLEDGE"
    NO_PARAMETERS_IN_SHOP_TITLE = "NO_PARAMETERS_IN_SHOP_TITLE"
    NO_SIZE_MEASURE = "NO_SIZE_MEASURE"
    UNKNOWN = "UNKNOWN"
    OTHER = "OTHER"


class WarehouseStockTypeEnum(str, Enum):
    AVAILABLE = 'AVAILABLE'                                                          # (соответствует типу «Доступный к заказу» в отчете «Остатки на складе» в личном кабинете магазина) — товар, доступный для продажи.
    DEFECT = 'DEFECT'                                                                # (соответствует типу «Брак») — товар с браком.
    EXPIRED = 'EXPIRED'                                                              # (соответствует типу «Просрочен») — товар с истекшим сроком годности.
    FIT = 'FIT'                                                                      # (соответствует типу «Годный») — товар, который доступен для продажи или уже зарезервирован.
    FREEZE = 'FREEZE'                                                                # — товар, который зарезервирован для заказов.
    QUARANTINE = 'QUARANTINE'                                                        # (соответсвует типу «Карантин») — товар, временно недоступный для продажи (например, товар перемещают из одного помещения склада в другое).
    UTILIZATION = 'UTILIZATION'                                                      # — товар, который будет утилизирован.
    SUGGEST = 'SUGGEST'                                                              # — товар, который рекомендуется поставить на склад (могут заказать в ближайшие две недели).
    TRANSIT = 'TRANSIT'                                                              # (соответствует типу «Продан») — проданный товар.


class ShopSkuStorageTypeEnum(str, Enum):
    FREE = 'FREE'
    PAID = 'PAID'


class ShopSkuStorageInclusionTypeEnum(str, Enum):
    FREE_EXPIRE = 'FREE_EXPIRE'
    PAID_EXPIRE = 'PAID_EXPIRE'
    PAID_EXTRA = 'PAID_EXTRA'


class TariffEntryEnum(str, Enum):
    AGENCY_COMMISSION = 'AGENCY_COMMISSION'                                          # прием и перечисление денег от покупателя (агентское вознаграждение).
    FULFILLMENT = 'FULFILLMENT'                                                      # обработка товара на складе Маркета.
    STORAGE = 'STORAGE'                                                              # хранение товара на складе Маркета в течение суток.
    SURPLUS = 'SURPLUS'                                                              # хранение излишков на складе Маркета.
    WITHDRAW = 'WITHDRAW'                                                            # вывоз товара со склада Маркета.
    FEE = 'FEE'                                                                      # размещение товара на Маркете.



class OrderStatsStatusType(str, Enum):
    CANCELLED_BEFORE_PROCESSING = 'CANCELLED_BEFORE_PROCESSING'                     # заказ отменен до начала его обработки.
    CANCELLED_IN_DELIVERY = 'CANCELLED_IN_DELIVERY'                                 # заказ отменен во время его доставки.
    CANCELLED_IN_PROCESSING = 'CANCELLED_IN_PROCESSING'                             # заказ отменен во время его обработки.
    DELIVERY = 'DELIVERY'                                                           # заказ передан службе доставки.
    DELIVERED = 'DELIVERED'                                                         # заказ доставлен.
    PARTIALLY_RETURNED = 'PARTIALLY_RETURNED'                                       # заказ частично возвращен покупателем.
    PICKUP = 'PICKUP'                                                               # заказ доставлен в пункт выдачи.
    PICKUP_SERVICE_RECEIVED = 'PICKUP_SERVICE_RECEIVED'
    PICKUP_USER_RECEIVED = 'PICKUP_USER_RECEIVED'                                   # покупатель получил заказ.
    PROCESSING = 'PROCESSING'                                                       # заказ в обработке.
    REJECTED = 'REJECTED'                                                           # заказ создан, но не оплачен.
    RETURNED = 'RETURNED'                                                           # заказ полностью возвращен покупателем.
    UNKNOWN = 'UNKNOWN'                                                             # неизвестный статус заказа
    INTAKE_SORTING = 'INTAKE_SORTING'                                                             # неизвестный статус заказа
    UNPAID = 'UNPAID'


class OrderEntryItemPriceTypeEnum(str, Enum):
    
    BUYER = 'BUYER'                                                                 # цена на товар с учетом скидок, в том числе купонов
    CASHBACK = 'CASHBACK'                                                           # баллы кешбэка по подписке Яндекс Плюс
    MARKETPLACE = 'MARKETPLACE'                                                     # купоны
    SPASIBO = 'SPASIBO'                                                             # бонусы СберСпасибо


class OrderStatsCommissionsTypeEnum(str, Enum):
    FEE = 'FEE'                                                                     # — размещение товара на Маркете;
    FULFILLMENT = 'FULFILLMENT'                                                     # — складская обработка;
    LOYALTY_PARTICIPATION_FEE = 'LOYALTY_PARTICIPATION_FEE'                         # — участие в программе лояльности и отзывы за баллы, если они подключены;
    AUCTION_PROMOTION = 'AUCTION_PROMOTION'                                         # — буст продаж;
    INSTALLMENT = 'INSTALLMENT'                                                     # — рассрочка;
    DELIVERY_TO_CUSTOMER = 'DELIVERY_TO_CUSTOMER'                                   # — доставка покупателю;
    EXPRESS_DELIVERY_TO_CUSTOMER = 'EXPRESS_DELIVERY_TO_CUSTOMER'                   # — экспресс-доставка покупателю;
    AGENCY = 'AGENCY'                                                               # — прием платежа покупателя;
    PAYMENT_TRANSFER = 'PAYMENT_TRANSFER'                                           # — перевод платежа покупателя;
    RETURNED_ORDERS_STORAGE = 'RETURNED_ORDERS_STORAGE'                             # — хранение невыкупов и возвратов;
    SORTING = 'SORTING'                                                             # — обработка заказа.
    INTAKE_SORTING = 'INTAKE_SORTING'                                               # — организация забора заказов со склада продавца.
    RETURN_PROCESSING = 'RETURN_PROCESSING'                                         # — обработка заказов на складе (FBY).


class ReportStatusType(str, Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    DONE = 'DONE'


class RegionType(str, Enum):
    OTHER = "OTHER"
    CONTINENT = "CONTINENT"
    REGION = "REGION"
    COUNTRY = "COUNTRY"
    COUNTRY_DISTRICT = "COUNTRY_DISTRICT"
    REPUBLIC = "REPUBLIC"
    CITY = "CITY"
    VILLAGE = "VILLAGE"
    CITY_DISTRICT = "CITY_DISTRICT"
    SUBWAY_STATION = "SUBWAY_STATION"
    REPUBLIC_AREA = "REPUBLIC_AREA"


class CampaignSettingsScheduleSourceType(str, Enum):
    WEB = "WEB"
    YML = "YML"

