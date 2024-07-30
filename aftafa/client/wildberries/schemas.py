from __future__ import annotations
from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Union, Dict
from enum import IntEnum

from pydantic import BaseModel, Field, constr
from aftafa.utils.helpers import to_camel


class Cursor(BaseModel):
    updatedAt: str
    nmID: int
    total: int


class Parameter(BaseModel):
    """ -- """
    count: Optional[int]
    units: Optional[str]
    value: Optional[str]


class AddIn(BaseModel):
    """Общие характеристики товара"""
    params: list[Parameter]
    type: str                               #


class Variation(BaseModel):
    """Структура с характеристиками различных размеров номенклатуры"""
    addin: list[AddIn]
    barcode: Optional[str]
    barcodes: list[str]
    chrtId: int
    errors: Union[list[str], None]
    id: UUID


class Nomenclature(BaseModel):
    """Структура с характеристиками номенклатур товара"""
    addin: list[AddIn]
    concatVendorCode: Optional[str]
    id: UUID
    isArchive: Optional[bool]
    nmId: int
    variations: list[Variation]
    vendorCode: str                         # Артикул товара

class Size(BaseModel):
    """
    """
    techSize: str
    wbSize: Optional[str]                   # Russian size
    price: Optional[int]
    chrtID: Optional[int]
    skus: list[str]

class Card(BaseModel):
    """Модель карточки"""
    nmID: int
    object: str
    brand: str
    vendorCode: str
    updateAt: datetime
    colors: list[str]
    mediaFiles: list[str]
    sizes: list[Size]


class RequestCardList(BaseModel):
    """/card/list HTTP response model"""
    class RequestCardListResult(BaseModel):
        """result field in the response"""
        cards: list[Card]
        cursor: Cursor
    
    data: RequestCardListResult
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[str]


class RequestCardListResult(BaseModel):
        """result field in the response"""
        cards: list[Card]
        cursor: Cursor


class RequestCardCursorList(BaseModel):
    """/card/list HTTP response model"""
    
    data: RequestCardListResult
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[str]


class RequestCardFilterResult(BaseModel):
        """result field in the response"""
        imtID: int
        nmID: int
        vendorCode: str
        mediaFiles: list[str]
        sizes: list[Size]
        characteristics: list[Dict[str, Union[int, str, list[str]]]]
        

class RequestCardFilter(BaseModel):
    """/card/filter HTTP response model"""
    
    data: list[RequestCardFilterResult]
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[str]


class Warehouse(BaseModel):
    """schema for a warehouse model from new API"""
    id: int
    office_id: Optional[int]
    name: str

    class Config:
        alias_generator = to_camel
        

class PriceInfo(BaseModel):
    """info on prices"""
    nmId: int
    price: int
    discount: int
    promoCode: int


class GetSuppliesSupplies(BaseModel):
    """
    """
    id: str                                                                     # Идентификатор поставки
    done: bool                                                                  # Флаг закрытия поставки
    createdAt: str	                                                            # Дата создания поставки (RFC3339)
    closedAt: Optional[str]                                                     # Дата закрытия поставки (RFC3339)
    scanDt: Optional[str]                                                       # Дата скана поставки (RFC3339)
    name: str                                                                   # Наименование поставки
    isLargeCargo: Optional[bool]                                                # сКГТ-признак поставки


class GetSupplies(BaseModel):
    """
    """
    next: int
    supplies: list[GetSuppliesSupplies]


class GetSuppliesSupplyOrdersSupplyOrderUser(BaseModel):
    fio: str
    phone: str


class GetSuppliesSupplyOrdersSupplyOrder(BaseModel):
    """
    """
    id: int                                                                     # Идентификатор сборочного задания в Маркетплейсе
    rid: str                                                                    # Идентификатор сборочного задания в системе Wildberries
    createdAt: str                                                              # Дата создания сборочного задания (RFC3339)
    warehouseId: int                                                            # Идентификатор склада поставщика, на который поступило сборочное задание
    prioritySc: list[str]                                                       # Массив приоритетных СЦ для доставки сборочного задания. Если поле не заполнено или массив пустой, приоритетного СЦ для данного сборочного задания нет.
    offices: Optional[list[str]]                                                # Список офисов, куда следует привезти товар.
    user: Optional[GetSuppliesSupplyOrdersSupplyOrderUser]                      # Информация о клиенте (только для доставки силами продавца)
    skus: list[str]                                                             # Массив штрихкодов товара
    price: int                                                                  # Цена в валюте продажи с учетом скидок в копейках. Код валюты продажи в поле currencyCode.
    convertedPrice: int                                                         # Цена продажи с учетом скидок в копейках, сконвертированная в рубли по курсу на момент создания сборочного задания. Предоставляется в информационных целях.
    currencyCode: int                                                           # Код валюты продажи (ISO 4217)
    convertedCurrencyCode: int                                                  # Код валюты страны поставщика (ISO 4217)
    orderUid: str                                                               # Идентификатор транзакции для группировки сборочных заданий. Сборочные задания в одной корзине клиента будут иметь одинаковый orderUID.
    nmId: int                                                                   # Артикул товара в системе Wildberries
    chrtId: int                                                                 # Идентификатор размера товара в системе Wildberries
    article: str                                                                # Артикул поставщика
    isLargeCargo: bool                                                          # сКГТ-признак товара, на который был сделан заказ


class GetSuppliesSupplyOrders(BaseModel):
    """
    """
    orders: list[GetSuppliesSupplyOrdersSupplyOrder]

# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------

class GetOrdersOrderAddress(BaseModel):
    """delivery address details"""
    province: str                               # Область
    area: str                                   # Район
    city: str                                   # Город
    street: str                                 # Улица
    home: str                                   # Номер дома
    flat: str                                   # 
    entrance: str                               #
    longitude: float
    latitude: float

    class Config:
        alias_generator = to_camel

class GetOrdersOrderUser(BaseModel):
    fio: str
    phone: str

    class Config:
        alias_generator = to_camel


class GetOrdersOrder(BaseModel):
    """
    """
    id: int                                                                     # Идентификатор сборочного задания в Маркетплейсе
    rid: str                                                                    # Идентификатор сборочного задания в системе Wildberries
    created_at: str                                                              # Дата создания сборочного задания (RFC3339)
    warehouse_id: int                                                            # Идентификатор склада поставщика, на который поступило сборочное задание
    supply_id: Optional[str]                                                     # Идентификатор поставки. Возвращается, если заказ закреплён за поставкой.
    priority_sc: Optional[list[str]]                                                       # Массив приоритетных СЦ для доставки сборочного задания. Если поле не заполнено или массив пустой, приоритетного СЦ для данного сборочного задания нет.
    offices: Optional[list[str]]                                                # Список офисов, куда следует привезти товар.
    address: Optional[GetOrdersOrderAddress]                                    # Детализованный адрес клиента для доставки (если применимо). Некоторые из полей могут прийти пустыми из-за специфики адреса.
    user: Optional[GetSuppliesSupplyOrdersSupplyOrderUser]                      # Информация о клиенте (только для доставки силами продавца)
    skus: list[str]                                                             # Массив штрихкодов товара
    price: str                                                                  # Цена в валюте продажи с учетом скидок в копейках. Код валюты продажи в поле currencyCode.
    converted_price: str                                                         # Цена продажи с учетом скидок в копейках, сконвертированная в рубли по курсу на момент создания сборочного задания. Предоставляется в информационных целях.
    currency_code: int                                                           # Код валюты продажи (ISO 4217)
    converted_currency_code: int                                                  # Код валюты страны поставщика (ISO 4217)
    order_uid: str                                                               # Идентификатор транзакции для группировки сборочных заданий. Сборочные задания в одной корзине клиента будут иметь одинаковый orderUID.
    delivery_type: str                                         # Тип доставки: fbs - доставка на склад Wildberries, dbs - доставка силами поставщика.
    nm_id: int                                                                   # Артикул товара в системе Wildberries
    chrt_id: int                                                                 # Идентификатор размера товара в системе Wildberries
    article: str                                                                # Артикул поставщика
    is_large_cargo: Optional[bool]                                                          # сКГТ-признак товара, на который был сделан заказ
    cargo_type: int                                                             # Тип товара: new
                                                                                #    1 - обычный
                                                                                #    2 - СГТ (Сверхгабаритный товар)
                                                                                #    3 - КГТ (Крупногабаритный товар). Не используется на данный момент

    class Config:
        alias_generator = to_camel

class GetOrders(BaseModel):
    """
    """
    next: int
    orders: list[GetOrdersOrder]

    class Config:
        alias_generator = to_camel

# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
class GetOrdersStickersSticker(BaseModel):
    """
    """
    order_id: int
    part_a: int
    part_b: int
    barcode: str
    file: str

    class Config:
        alias_generator = to_camel

class GetOrdersStickers(BaseModel):
    """
    """
    stickers: Optional[list[GetOrdersStickersSticker]]










# --------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
class OrderStatusEnum(IntEnum):
    NEW_ORDER = 0                           # Новый заказ
    ACCEPTED = 1                            # Принял заказ
    COMPLETED = 2                           # Сборочное задание завершено
    REJECTED = 3                            # Сборочное задание отклонено
    INDELIVERY = 5                          # На доставке курьером
    DELIVERED = 6                           # Курьер довез и клиент принял товар
    CUSTOMER_REJECTED = 7                   # Клиент не принял товар
    PICKUP_PROCESSED = 8                    # Товар для самовывоза из магазина принят к работе
    PICKUP_READY = 9                        # Товар для самовывоза из магазина готов к выдаче


class OrderUserStatusEnum(IntEnum):
    NEW_ORDER = 0                           # Новый заказ
    CUSTOMER_CANCELLED = 1                  # Отмена клиента
    DELIVERED = 2                           # Доставлен
    RETURN = 3                              # Возврат
    AWAITING = 4                            # Ожидает
    FAULTY = 5                              # Брак


class CurrencyCodeEnum(IntEnum):
    AMD = 51                                      # Армянский драм
    KZT = 398                                     # Казахский тенге
    KGS = 417                                     # Киргизский сом
    RUB = 643                                     # Российский рубль
    USD = 840                                     # Доллар США
    BYN = 933                                     # Белорусский рубль
    BYR = 974                                     # Белорусский рубль
    UZS = 860                                     # Uzbekistan sum


class DeliveryTypeEnum(IntEnum):
    DELIVERY = 1                                  # обычная доставка
    DELIVERY_BY_SELLER = 2                        # доставка силами поставщика


class UserInfo(BaseModel):
    """user info"""
    userId: Optional[int]
    fio: str
    email: str
    phone: str


class Order(BaseModel):
    """order schema"""
    orderId: constr(max_length=32)                      # Идентификатор заказа
    dateCreated: datetime                               # Дата создания заказа (RFC3339) example: 2021-02-20T16:50:33.365+03:00
    wbWhId: int                                         # Идентификатор склада WB, на которой заказ должен быть доставлен
    storeId: int                                        # Идентификатор склада поставщика, на который пришел заказ.
    pid: int                                            # Идентификатор ПВЗ/магазина, куда необходимо доставить заказ (если применимо)
    officeAddress: str                                  # 
    deliveryAddress: str                                # 
    # deliveryAddressDetails: DeliveryAddressDetails      # 
    userInfo: UserInfo                                  # 
    chrtId: int                                         #
    barcode: str                                        #
    barcodes: list[str]                                 #
    scOfficesNames: list[Union[str, None]]              # Массив СЦ приоритетных для доставки заказа. Если поле не заполнено или массив пустой, приоритетного СЦ нет для данного заказа нет.
    status: OrderStatusEnum                             # 
    userStatus: OrderUserStatusEnum                     # 
    rid: constr(max_length=32)                          # Уникальный идентификатор вещи, разный у одинаковых chrt_id
    totalPrice: int                                     # Цена в валюте продажи с учетом скидок в копейках. Код валюты продажи в поле currencyCode
    convertedPrice: int                                 # Цена продажи с учетом скидок, сконвертированная в рубли по курсу на момент создания заказа. Предоставляется в информационных целях.
    currencyCode: CurrencyCodeEnum                      # Код валюты по ISO 4217
    orderUID: str                                       # Идентификатор транзакции для группировки заказов. Заказы в одной корзине клиента будут иметь одинаковый orderUID
    deliveryType: DeliveryTypeEnum                      # Тип доставки









class OrdersAPIResponse(BaseModel):
    """response with orders (new API)"""
    total: int
    orders: list[Order]


class SupplierStocks(BaseModel):
    """"stock maps from /api/v1/supplier/stocks method"""
    last_change_date: str
    warehouse_name: constr(max_length=50)
    supplier_article: constr(max_length=75)
    nm_id: int
    barcode: constr(max_length=30)
    quantity: int
    in_way_to_client: int
    in_way_from_client: int
    quantity_full: int
    category: constr(max_length=50)
    subject: constr(max_length=50)
    brand: constr(max_length=50)
    tech_size: constr(max_length=30)
    price: float = Field(alias='Price')
    discount: float = Field(alias='Discount')
    is_supply: bool
    is_realization: bool
    sc_code: constr(max_length=50) = Field(alias='SCCode')

    class Config:
        alias_generator = to_camel


class SupplierOrders(BaseModel):
    """"order maps from /api/v1/supplier/orders method"""
    date: datetime                                          # дата заказа
    lastChangeDate: datetime                                # дата время обновления информации в сервисе
    supplierArticle: constr(max_length=75)                  # ваш артикул 
    techSize: constr(max_length=30)                         # размер
    barcode: constr(max_length=30)                          # штрих-код
    totalPrice: int                                         # цена до согласованной скидки/промо/спп
    discountPercent: int                                    # согласованный итоговый дисконт
    warehouseName: constr(max_length=50)                    # склад отгрузки
    countryName: constr(max_length=200)
    oblastOkrugName: constr(max_length=200)                          # область
    regionName: constr(max_length=200)
    incomeID: int                                           # номер поставки
    # odid: int                                               # уникальный идентификатор позиции заказа (номер уникальной позиции заказа – odid (rid))
    nmId: int                                               # Код WB
    subject: constr(max_length=50)
    category: constr(max_length=50)
    brand: constr(max_length=50)
    isCancel: bool
    isSupply: bool
    isRealization: bool
    spp: float
    finishedPrice: float
    priceWithDisc: float
    orderType: str
    cancelDate: datetime
    gNumber: constr(max_length=50)                          # Для идентификации товаров, из одного заказа, и продаж по ним необходимо использовать поле gNumber
    sticker: constr(max_length=50)                          # аналогично стикеру, который клеится на товар в процессе сборки
    srid: constr(max_length=50)                             # srid


class SupplierOrdersV2(BaseModel):
    """"order maps from /api/v1/supplier/orders method"""
    date: str                                          # дата заказа
    last_change_date: str                                # дата время обновления информации в сервисе
    warehouse_name: constr(max_length=50)                    # склад отгрузки
    country_name: constr(max_length=200)
    oblast_okrug_name: constr(max_length=200)                          # область
    region_name: constr(max_length=200)
    supplier_article: constr(max_length=75)                  # ваш артикул 
    nm_id: int                                               # Код WB
    barcode: constr(max_length=30)                          # штрих-код
    category: constr(max_length=50)
    subject: constr(max_length=50)
    brand: constr(max_length=50)
    tech_size: constr(max_length=30)                         # размер
    income_ID: int                                           # номер поставки
    is_supply: bool
    is_realization: bool
    total_price: int                                         # цена до согласованной скидки/промо/спп
    discount_percent: int                                    # согласованный итоговый дисконт
    spp: float
    finished_price: float
    price_with_disc: float
    is_cancel: bool
    cancel_date: str
    order_type: str
    sticker: constr(max_length=50)                          # аналогично стикеру, который клеится на товар в процессе сборки
    g_number: constr(max_length=50)                          # Для идентификации товаров, из одного заказа, и продаж по ним необходимо использовать поле gNumber
    srid: constr(max_length=50)                             # srid

    class Config:
        alias_generator = to_camel


class SupplierSales(BaseModel):
    """"sales maps from /api/v1/supplier/sales method"""
    date: str                                          # дата заказа
    last_change_date: str                                # дата время обновления информации в сервисе
    supplier_article: constr(max_length=75)                  # ваш артикул 
    tech_size: constr(max_length=30)                         # размер
    barcode: constr(max_length=30)                          # штрих-код
    total_price: int                                         # цена до согласованной скидки/промо/спп
    discount_percent: int                                    # согласованный итоговый дисконт
    is_supply: bool                                          # договор поставки
    is_realization: bool                                     # договор реализации
    warehouse_name: constr(max_length=50)                    # склад отгрузки
    country_name: constr(max_length=200)                     # страна
    oblast_okrug_name: constr(max_length=200)                 # область/округ
    region_name: constr(max_length=200)                      # регион
    income_ID: Optional[int]                                 # номер поставки
    sale_ID: constr(max_length=15)                           # уникальный идентификатор продажи/возврата (SXXXXXXXXXX — продажа, RXXXXXXXXXX —
                                                            # возврат, DXXXXXXXXXXX — доплата, 'AXXXXXXXXX' – сторно продаж (все значения полей как у
                                                            # продажи, но поля с суммами и кол-вом с минусом как в возврате). SaleID='BXXXXXXXXX' - сторно
                                                            # возврата(все значения полей как у возврата, но поля с суммами и кол-вом с плюсом, в
                                                            # противоположность возврату
    # odid: int                                               # уникальный идентификатор позиции заказа (номер уникальной позиции заказа – odid (rid)
    spp: float                                              # согласованная скидка постоянного покупателя (СПП)
    for_pay: float                                           # к перечислению поставщику
    finished_price: int                                      # фактическая цена из заказа (с учетом всех скидок, включая и от ВБ)
    price_with_disc: float                                    # цена, от которой считается вознаграждение поставщика forpay (с учетом всех согласованных скидок)
    nm_id: int                                               # Код WB
    subject: constr(max_length=50)
    category: constr(max_length=50)
    brand: constr(max_length=50)
    is_storno: Optional[bool]
    g_number: constr(max_length=50)                          # Для идентификации товаров, из одного заказа, и продаж по ним необходимо использовать поле gNumber
    sticker: constr(max_length=50)                          # аналогично стикеру, который клеится на товар в процессе сборки
    srid: constr(max_length=50)                             # srid

    class Config:
        alias_generator = to_camel


class SupplierFinReport(BaseModel):
    """detailed report by period """
    realizationreport_id: Optional[int]                               # Номер отчета
    date_from: Optional[str]                                          # Дата начала отчетного периода
    date_to: Optional[str]                                            # Дата конца отчетного периода
    create_dt: Optional[str]                                          # Дата формирования отчёта
    suppliercontract_code: Optional[int]                    # Договор
    rid: Optional[int]                                                # Уникальный идентификатор позиции заказа
    rr_dt: Optional[str]                                              # Дата операции. Присылается с явным указанием часового пояса.
    rrd_id: Optional[int]                                             # Номер строки
    gi_id: Optional[int]                                              # Номер поставки
    subject_name: Optional[str]                             # Предмет
    nm_id: Optional[int]                                    # Артикул
    brand_name: Optional[str]                               # Бренд
    sa_name: Optional[str]                                  # Артикул поставщика
    ts_name: Optional[str]                                  # Размер
    barcode: Optional[str]                                  # Бар-код
    doc_type_name: Optional[str]                                      # Enum: "Продажа" "Возврат" Тип документа
    quantity: Optional[int]                                           # Количество
    retail_price: Optional[float]                                     # Цена розничная
    retail_amount: Optional[float]                                    # Сумма продаж (возвратов)
    sale_percent: Optional[int]                                       # Согласованная скидка
    commission_percent: Optional[float]                               # Процент комиссии
    office_name: Optional[str]                              # Склад
    supplier_oper_name: str                                 # Обоснование для оплаты
    order_dt: Optional[str]                                           # Дата заказа. Присылается с явным указанием часового пояса.
    sale_dt: Optional[str]                                            # Дата продажи. Присылается с явным указанием часового пояса.
    shk_id: Optional[int]                                             # Штрих-код
    retail_price_withdisc_rub: Optional[float]                        # Цена розничная с учетом согласованной скидки
    delivery_amount: Optional[int]                                    # Количество доставок
    return_amount: Optional[int]                                      # Количество возвратов
    delivery_rub: Optional[float]                                     # Стоимость логистики
    gi_box_type_name: Optional[str]                                   # Тип коробов
    product_discount_for_report: Optional[float]                      # Согласованный продуктовый дисконт
    supplier_promo: Optional[float]                                   # Промокод
    ppvz_spp_prc: Optional[float]                                     # Скидка постоянного покупателя
    ppvz_kvw_prc_base: Optional[float]                                # Размер кВВ без НДС, % базовый
    ppvz_kvw_prc: Optional[float]                                     # Итоговый кВВ без НДС, %
    sup_rating_prc_up: Optional[float]                                # Размер снижения кВВ из-за рейтинга, % new
    is_kgvp_v2: Optional[float]                                       # Размер снижения кВВ из-за акции, % new
    ppvz_sales_commission: Optional[float]                            # Вознаграждение с продаж до вычета услуг поверенного, без НДС
    ppvz_for_pay: Optional[float]                                     # К перечислению продавцу за реализованный товар
    ppvz_reward: Optional[float]                                      # Возмещение расходов услуг поверенного
    acquiring_fee: Optional[float]                                    # Возмещение расходов по эквайрингу.
                                                            # Расходы WB на услуги эквайринга: вычитаются из вознаграждения WB и не влияют на доход продавца.
    acquiring_bank: Optional[str]                           # Наименование банка, предоставляющего услуги эквайринга
    ppvz_vw: Optional[float]                                          # Вознаграждение WB без НДС
    ppvz_vw_nds: Optional[float]                                      # НДС с вознаграждения WB
    ppvz_office_id: Optional[int]                                     # Номер офиса
    ppvz_office_name: Optional[str]                                   # Наименование офиса доставки
    ppvz_supplier_id: Optional[int]                                   # Номер партнера
    ppvz_supplier_name: Optional[str]                                 # Партнер
    ppvz_inn: Optional[str]                                           # ИНН партнера
    declaration_number: Optional[str]                                 # Номер таможенной декларации
    sticker_id: Optional[str]                                         # Цифровое значение стикера, который клеится на товар в процессе сборки заказа по системе Маркетплейс.
    site_country: Optional[str]                                       # Страна продажи
    penalty: Optional[float]                                          # Штрафы
    additional_payment: Optional[float]                               # Доплаты
    bonus_type_name: Optional[str]                                    # Обоснование штрафов и доплат
    rebill_logistic_cost: Optional[float]                   # Возмещение издержек по перевозке
    rebill_logistic_org: Optional[str]                      # Организатор перевозки
    srid: Optional[str]                                               # Уникальный идентификатор заказа, функционально аналогичный odid/rid. 
                                # Данный параметр введен в июле'22 и в течение переходного периода может быть заполнен не во всех ответах.
                                # Примечание для работающих по системе Маркетплейс: srid равен rid в ответе на метод GET /api/v2/orders.
    currency_name: Optional[str]
    kiz: Optional[str]

class BalancesTableCell(BaseModel):
    value: str
    colspan: int


class BalancesTableCellHolder(BaseModel):
    cells: Optional[list[BalancesTableCell]]


class BalancesTable(BaseModel):
    count: int
    data: list[list[str]]
    headerExcel: list[BalancesTableCellHolder]
    headerFront: list[BalancesTableCellHolder]


class PostBackV1BalancesResponseData(BaseModel):
    table: BalancesTable


class PostBackV1BalancesResponse(BaseModel):
    """/v1/balances HTTP response model"""
    
    data: Optional[PostBackV1BalancesResponseData]
    error: bool
    errorText: Optional[str]
    additionalErrors: Optional[str]


class PostStocksByWarehouseResponseStocks(BaseModel):
    sku: str
    amount: int


class PostStocksByWarehouseResponse(BaseModel):
    """"""
    stocks: list[Optional[PostStocksByWarehouseResponseStocks]]

# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
class V2CardPhoto(BaseModel):
    size1: str = Field(alias='c246x328')
    size2: str = Field(alias='c516x688')
    big: str
    square: str
    tm: str

class V2CardDimensions(BaseModel):
    length: int
    width: int
    height: int


class V2CardCharacteristics(BaseModel):
    id: int
    name: str
    value: Any


class V2CardTag(BaseModel):
    id: int
    name: str
    color: str


class ContentV2GetCardsListCard(BaseModel):
    """Модель карточки"""
    nm_ID: int
    imt_ID: int
    subject_ID: int
    vendor_code: str
    subject_name: str
    brand: str
    title: str
    photos: Optional[list[V2CardPhoto]]
    video: Optional[str]
    dimensions: Optional[V2CardDimensions]
    characteristics: Optional[list[V2CardCharacteristics]]
    sizes: Optional[list[Size]]
    tags: Optional[list[V2CardTag]]
    created_at: str
    updated_at: str

    class Config:
        alias_generator = to_camel


class PostContentV2GetCardsListResponse(BaseModel):
    cards: Optional[list[ContentV2GetCardsListCard]]
    cursor: Cursor


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
class V2ListGoodsFilterDataGoodsListSize(BaseModel):
    size_ID: int
    price: int
    discounted_price: float
    tech_size_name: str

    class Config:
        alias_generator = to_camel


class V2ListGoodsFilterDataGoodsList(BaseModel):
    nm_ID: int
    vendor_code: str
    sizes: Optional[list[V2ListGoodsFilterDataGoodsListSize]]
    currency_iso_code_4217: str
    discount: int
    editable_size_price: bool

    def to_dict(self) -> dict:
        size_cont = []
        repr_ = self.dict()
        for size_ in repr_.get('sizes'):
            size_repr = {k: v for k, v in repr_.items()}
            size_repr.pop('sizes')
            size_repr['nomenclature_id'] = size_repr['nm_ID']
            size_repr['currency_code'] = size_repr['currency_iso_code_4217']
            size_repr['variation_id'] = size_['size_ID']
            size_repr['price'] = size_['price']
            size_repr['discounted_price'] = size_['discounted_price']
            size_repr['tech_size_name'] = size_['tech_size_name']
            size_cont.append(size_repr)
        return size_cont


    class Config:
        alias_generator = to_camel



class V2ListGoodsFilterData(BaseModel):
    list_goods: Optional[list[V2ListGoodsFilterDataGoodsList]]

    class Config:
        alias_generator = to_camel


class GetV2ListGoodsFilterResponse(BaseModel):
    data: V2ListGoodsFilterData


# GetOrdersOrder.update_forward_refs()
RequestCardListResult.update_forward_refs()
RequestCardCursorList.update_forward_refs()
RequestCardFilter.update_forward_refs()


# GetSuppliesSupplyOrdersSupplyOrderUser.update_forward_refs()
# GetOrdersOrderAddress.update_forward_refs()