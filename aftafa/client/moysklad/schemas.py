from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional, Literal, Union, Any
from pydantic import BaseModel, Field, constr


def to_lower(string: str) -> str:
    indices = []
    ct: int = 0

    for i, char in enumerate(string):
        if not char.islower():
            k: int = 1
            while (i + k) < len(string):
                if ct == 0:
                        indices.append(string[:i])
                if not string[(k + i)].islower():
                    indices.append(string[i:(k + i)])
                    break
                if (i + k + 1) == len(string):
                    indices.append(string[i:(i + k + 1)])
                k += 1
                ct += 1

    return '_'.join([ind.lower() for ind in indices])

def to_camel(string: str) -> str:
    string = ''.join(word.capitalize() for word in string.split('_'))
    return (string[0].lower() + string[1:])

def convert_datetime(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class Meta(BaseModel):
    """Essential class in Moysklad, serves as a link to an object in the system. It can link with
    it via either href (reference) or an id of the object."""
    href: str                              # a reference to the object
    metadatadaHref: Optional[str]          # a reference to the object's metada if it exists
    type: constr(max_length=255)
    mediaType: constr(max_length=255)          # almost always 'application/json'
    uuidHref: Optional[str]
    downloadHref: Optional[str]
    size: Optional[int]
    limit: Optional[int]
    offset: Optional[int]


class Error(BaseModel):
    """Ошибка в данном API представляет собой массив errors, содержащий объекты error, каждый из которых описывает отдельную ошибку."""
    error: constr(max_length=255)
    parameter: constr(max_length=255)
    code: int
    error_message: constr(max_length=255)


class AttributeTypeEnum(str, Enum):
    """Enum type for attributes""" 
    TIME = "time"
    LINK = "link"
    STRING = "string"
    TEXT = "text"
    FILE = "file"
    BOOLEAN = "boolean"
    DOUBLE = "double"
    LONG = "long"
    CUSTOM_ENTITY = "customentity"


class MetaArray(BaseModel):
    """Array of Meta objects"""
    meta : Meta
    value : Optional[Any]
    rows : Optional[list[Meta]]


class Attribute(BaseModel):
    """Посмотреть все созданные доп. поля можно с помощью запроса на получение метаданных сущности. 
    Ответ будет содержать описание доп. полей в виде коллекции attributes, если указанная сущность поддерживает 
    работу с доп. полями."""
    class AttributeMetaValue(BaseModel):
        """meta dictionary for attributes"""
        meta: Meta

    description: Optional[constr(max_length=4096)]
    id: UUID
    meta: Meta
    customEntityMeta: Optional[Meta]         #Если в качестве типа доп. поля выбран Пользовательский справочник, то в составе объекта данного доп. поля появится новый атрибут customEntityMeta являющийся ссылкой на метаданные этого справочника. Полный набор атрибутов доп. поля будет выглядеть следующим образом
    name: constr(max_length=255)
    required: Optional[bool]
    show: Optional[bool]
    type: AttributeTypeEnum
    value: Optional[Union[MetaArray, str, int, bool]]


class CustomEntity(BaseModel):
    """basic customentity"""
    meta: Meta
    entity_meta: Meta
    name: constr(max_length=255)
    create_shared: bool

    class Config:
        alias_generator = to_camel


class CustomEntityMember(BaseModel):
    """basic customentity member"""
    meta: Meta
    id: UUID
    account_id: UUID
    updated: datetime
    name: constr(max_length=255)
    code: Optional[str]
    external_code: str
    owner: MetaArray
    group: MetaArray
    shared: bool

    class Config:
        alias_generator = to_camel


class RateMetaArray(BaseModel):
    """Array of Meta objects for rates"""
    currency : MetaArray


class TaxSystemEnum(str, Enum):
    """Enum type for the tax system field of the customer order model"""
    GENERAL_TAX_SYSTEM = 'GENERAL_TAX_SYSTEM'       #ОСН
    PATENT_BASED = 'PATENT_BASED'        #Патент
    PRESUMPTIVE_TAX_SYSTEM = 'PRESUMPTIVE_TAX_SYSTEM'      #ЕНВД
    SIMPLIFIED_TAX_SYSTEM_INCOME = 'SIMPLIFIED_TAX_SYSTEM_INCOME'        #УСН. Доход
    SIMPLIFIED_TAX_SYSTEM_INCOME_OUTCOME = 'SIMPLIFIED_TAX_SYSTEM_INCOME_OUTCOME'        #УСН. Доход-Расход
    TAX_SYSTEM_SAME_AS_GROUP = 'TAX_SYSTEM_SAME_AS_GROUP'        #Совпадает с группой
    UNIFIED_AGRICULTURAL_TAX = 'UNIFIED_AGRICULTURAL_TAX'        #ЕСХН


class SalesChannelEnum(str, Enum):
    """This enum is for sales channels"""
    MESSENGER = "MESSENGER"         #Мессенджер
    SOCIAL_NETWORK = "SOCIAL_NETWORK"           #Социальная сеть
    MARKETPLACE = "MARKETPLACE"         #Маркетплейс
    ECOMMERCE = "ECOMMERCE"         #Интернет-магазин
    CLASSIFIED_ADS = "CLASSIFIED_ADS"       #Доска объявлений
    DIRECT_SALES = "DIRECT_SALES"        #Прямые продажи
    OTHER = "OTHER"       #Другое


class TrackingTypeEnum(str, Enum):
    """This enum is for tracking type of a product if it exists"""
    ELECTRONICS = 'ELECTRONICS'         #Фотокамеры и лампы-вспышки
    LP_CLOTHES = 'LP_CLOTHES'          #Тип маркировки "Одежда"
    LP_LINENS = 'LP_LINENS'           #Тип маркировки "Постельное белье"
    MILK = 'MILK'            #Молочная продукция
    NCP = 'NCP'         #Никотиносодержащая продукция
    NOT_TRACKED = 'NOT_TRACKED'         #Без маркировки
    OTP = 'OTP'         #Альтернативная табачная продукция
    PERFUMERY = 'PERFUMERY'           #Духи и туалетная вода
    SHOES = 'SHOES'           #Тип маркировки "Обувь"
    TIRES = 'TIRES'         #Шины и покрышки
    TOBACCO = 'TOBACCO'         #Тип маркировки "Табак"
    WATER = 'WATER'       #Упакованная вода


class PaymentItemTypeEnum(str, Enum):
    """This enum is for payment item type of a product if it exists"""
    GOOD = 'GOOD'         #Товар
    EXCISABLE_GOOD = 'EXCISABLE_GOOD'          #Подакцизный товар
    COMPOUND_PAYMENT_ITEM = 'COMPOUND_PAYMENT_ITEM'           #Составной предмет расчета
    ANOTHER_PAYMENT_ITEM = 'ANOTHER_PAYMENT_ITEM'            #Иной предмет расчета


class ActualAddressEntity(BaseModel):
    """Строка адреса является конкатенацией полей структурированного адреса в следующем порядке: 
    postalCode -> country -> region -> city -> street -> house -> apartment -> addInfo, используя запятую 
    в качестве разделителя."""
    addInfo : Optional[str]
    apartment : Optional[str]
    city : Optional[str]
    comment : Optional[str]
    country : Optional[MetaArray]
    house : Optional[str]
    postalCode : Optional[str]
    region : Optional[MetaArray]
    street : Optional[str]


class Assortment(BaseModel):
    """Сущность assortment представляет собой список всех товаров, услуг, комплектов, серий и модификаций с полями stock, reserve,
    inTransit, quantity, показывающими остаток, резерв, ожидание и доступно каждой из сущностей (для комплектов и услуг эти поля не 
    выводятся). Данные поля могут быть рассчитаны в зависимости от даты и склада с использованием параметров фильтрации 
    stockMoment и stockStore."""
    archived : bool
    article : str
    barcode : str
    code : str


class ProductFolderEntity(BaseModel):
    """Средствами JSON API можно создавать и обновлять сведения о Группах товаров, запрашивать списки Групп товаров и 
    сведения по отдельным Группам товаров. Кодом сущности для Группы товаров в составе JSON API является ключевое 
    слово productfolder """
    account_id : UUID = Field(alias='accountId')
    archived : bool
    code : Optional[str]
    description : Optional[str]
    effective_vat : Optional[int] = Field(alias='effectiveVat')
    effective_vat_enabled : Optional[bool] = Field(alias='effectiveVatEnabled')
    external_code : str = Field(alias='externalCode')
    group : MetaArray
    id : UUID
    meta : Meta
    name : str
    owner : MetaArray
    path_name : str = Field(alias='pathName')
    product_folder : Optional[MetaArray] = Field(alias='productFolder')
    shared : bool
    tax_system : Optional[TaxSystemEnum] = Field(alias='taxSystem')
    updated : datetime
    use_parent_vat : bool = Field(alias='useParentVat')
    vat : Optional[int]
    vat_enabled : Optional[bool] = Field(alias='vatEnabled')

    class Config:
        orm_mode = True


class ContractEntity(BaseModel):
    """Кодом сущности для Договора в составе JSON API является ключевое слово contract"""
    account_id : UUID
    agent : MetaArray
    agent_account : Optional[Meta]
    archived : bool
    attributes : Optional[list[Attribute]]
    code : Optional[str]
    contract_type : Literal["Commission", "Sales"]
    description : Optional[str]
    external_code : str
    group : MetaArray
    id : UUID
    meta : Meta
    moment : datetime
    name : str
    organization_account : Optional[Meta]
    own_agent : MetaArray
    owner : MetaArray
    rate : RateMetaArray
    reward_percent : int
    reward_type : Optional[str]
    shared : bool
    state : MetaArray
    sum : int
    updated : datetime

    class Config:
        alias_generator = to_camel


class CounterpartyEntity(BaseModel):
    """Счетами Контрагента и его контактными лицами можно управлять как в составе отдельного Контрагента, так и 
    отдельно - с помощью специальных ресурсов для управления счетами и контактными лицами Контрагента. Кодом 
    сущности для Контрагента в составе JSON API является ключевое слово counterparty."""
    account_id : UUID
    accounts : MetaArray
    actual_address : Optional[str]
    actual_address_full : Optional[ActualAddressEntity]
    attributes : Optional[list[Attribute]]
    archived : bool
    bonus_points : Optional[int]
    bonus_program : Optional[Meta]
    certificate_date : Optional[datetime]
    certificate_number : Optional[str]
    code : Optional[str]
    contactpersons : Optional[MetaArray]
    company_type : Literal["legal", "entrepreneur", "individual"]
    created : datetime
    description : Optional[str]
    discounts : Optional[str]
    discount_card_number : Optional[str]
    email : Optional[str]
    external_code : str
    fax : Optional[str]
    files : MetaArray
    group : MetaArray
    id : UUID
    inn : Optional[str]
    kpp : Optional[str]
    legal_address : Optional[str]
    legal_address_full : Optional[ActualAddressEntity]
    legal_first_name : Optional[str]
    legal_last_name : Optional[str]
    legal_middle_name : Optional[str]
    legal_title : Optional[str]
    meta : Meta
    name : str
    notes : MetaArray
    ogrn : Optional[str]
    ogrnip : Optional[str]
    okpo : Optional[str]
    owner : Optional[MetaArray]
    phone : Optional[str]
    sales_amount : int
    shared : bool
    state : Optional[MetaArray]
    sync_id : Optional[UUID]
    tags : Optional[list[str]]
    updated : datetime

    class Config:
        alias_generator = to_camel


class OrganizationEntity(BaseModel):
    """С помощью специального ресурса можно управлять счетами отдельного юрлица. Кодом сущности для юрлица в составе JSON API является ключевое слово organization. 
    По данной сущности можно осуществлять контекстный поиск с помощью специального параметра search."""
    account_id : UUID
    actual_address : Optional[str]
    actual_address_full : Optional[ActualAddressEntity]
    archived : bool
    attributes : Optional[list[Attribute]]
    bonus_points : Optional[int]
    bonus_program : Optional[Meta]
    certificate_date : Optional[datetime]
    certificate_number : Optional[str]
    chief_accountSign : Optional[str]        #TODO: actually not a string!
    chief_accountant : Optional[str]
    code : Optional[str]
    company_type : Literal["legal", "entrepreneur", "individual"]
    created : datetime
    description : Optional[str]
    director : Optional[str]
    director_position : Optional[str]
    director_sign : Optional[str]            #TODO: actually not a string!
    email : Optional[str]
    external_code : str
    fax : Optional[str]
    fsrar_id : Optional[str]         #Идентификатор в ФСРАР
    group : MetaArray
    id : UUID
    inn : Optional[str]
    is_egais_enable : bool        #Включен ли ЕГАИС для данного юрлица
    kpp : Optional[str]
    legal_address : Optional[str]
    legal_address_full : Optional[ActualAddressEntity]
    legal_first_name : Optional[str]
    legal_last_name : Optional[str]
    legal_middle_name : Optional[str]
    legal_title : Optional[str]
    meta : Meta
    name : str
    ogrn : Optional[str]
    ogrnip : Optional[str]
    okpo : Optional[str]
    owner : Optional[MetaArray]
    payer_vat : bool
    shared : bool
    sync_id : Optional[UUID]
    tracking_contract_date : Optional[datetime]
    tracking_contract_number : Optional[str]
    updated : datetime

    class Config:
        alias_generator = to_camel


class GroupEntity(BaseModel):
    """Кодом сущности для Отдела в составе JSON API является ключевое слово group."""
    account_id: UUID
    id: UUID
    index: int
    meta: Meta
    name: str

    class Config:
        alias_generator = to_camel


class ProjectEntity(BaseModel):
    """Кодом сущности для Проекта в составе JSON API является ключевое слово project."""
    accountId : UUID
    archived : bool
    attributes : Optional[list[Attribute]]
    code : Optional[str]
    description : Optional[str]
    externalCode : str
    group : MetaArray
    id : UUID
    meta : Meta
    name : str
    owner : Optional[MetaArray]
    shared : bool
    updated : datetime


class StoreEntity(BaseModel):
    """Сущность для работы со складами. По данной сущности можно осуществлять контекстный поиск с 
    помощью специального параметра search"""
    account_id : UUID
    address : Optional[str]
    address_full : Optional[ActualAddressEntity]
    archived : bool
    attributes : Optional[list[Attribute]]
    code : Optional[str]
    description : Optional[str]
    external_code : str
    group : MetaArray
    id : UUID
    meta : Meta
    name : str
    owner : Optional[MetaArray]
    parent : Optional[Meta]
    path_name : Optional[str]
    shared : bool
    updated : datetime

    class Config:
        alias_generator = to_camel


class EmployeeEntity(BaseModel):
    """Сущность для работы с сотрудниками. Средствами JSON API можно запрашивать списки Сотрудников и сведения по отдельным Сотрудникам.
    По данной сущности можно осуществлять контекстный поиск с помощью специального параметра search"""
    account_id : UUID
    archived : bool
    attributes : Optional[list[Attribute]]
    cashiers : Optional[list[MetaArray]]
    code : Optional[str]
    created : datetime
    description : Optional[str]
    email : Optional[str]
    external_code : str
    first_name : Optional[str]
    full_name : Optional[str]
    group : MetaArray
    id : UUID
    inn : Optional[str]
    last_name : Optional[str]
    meta : Meta
    middle_name : Optional[str]
    name : str
    owner : Optional[MetaArray]
    phone : Optional[Union[Meta, str]]
    position : Optional[str]
    shared : bool
    short_fio : Optional[str]
    uid : Optional[str]
    updated : datetime

    class Config:
        alias_generator = to_camel


class ProductEntity(BaseModel):
    """Кодом сущности для Товара в составе JSON API является ключевое слово product.
    По данной сущности можно осуществлять контекстный поиск с помощью специального параметра search.
    Поиск среди объектов товаров на соответствие поисковой строке будет осуществлен по следующим полям:
            по наименованию товара (name)
            по коду товара (code)
            по артикулу (article)"""
    class BuyPrice(BaseModel):
        """Buy price for a product"""
        value : float
        currency : MetaArray

    class MinPrice(BaseModel):
        """Minimum price for a product"""
        value : float
        currency : MetaArray

    class SalePrice(BaseModel):
        """Sale prices for a product"""
        value : float
        currency : MetaArray
        price_type : MetaArray

        class Config:
            alias_generator = to_camel

    class Pack(BaseModel):
        """Packs for a product"""
        barcodes : list[dict]
        id : UUID
        quantity : float
        uom : Meta

    account_id : UUID
    alcoholic : Optional[bool]
    archived : bool
    article : Optional[str]
    attributes : Optional[list[Attribute]]
    barcodes : Optional[list[dict]]
    buy_price : BuyPrice
    code : Optional[str]
    country : Optional[MetaArray]
    description : Optional[str]
    discount_prohibited : bool
    effective_vat : Optional[int]
    effective_vat_enabled : Optional[bool]
    external_code : str
    files : Optional[MetaArray]
    group : MetaArray
    id : UUID
    images : Optional[MetaArray]
    is_serial_trackable : bool        #Учет по серийным номерам. Не может быть указан вместе с alcoholic и weighed
    meta : Meta
    min_price : MinPrice
    minimum_balance : Optional[int]
    name : str
    owner : MetaArray
    packs : Optional[list[Pack]]          #Упаковки Товара
    partial_disposal : Optional[bool]      #Управление состоянием частичного выбытия маркированного товара. «true» - возможность включена.
    path_name : str
    payment_item_type : PaymentItemTypeEnum
    ppe_type : Optional[str]
    product_folder : Optional[MetaArray]
    sale_prices : list[SalePrice]
    shared : bool
    supplier : Optional[MetaArray]
    sync_id : Optional[UUID]
    tax_system : Optional[TaxSystemEnum]
    things : Optional[list[str]]      #Серийные номера
    tnved : Optional[str]     #Код ТН ВЭД
    tracking_type : TrackingTypeEnum
    uom : Optional[MetaArray]
    updated : datetime
    use_parent_vat : bool
    variants_count : int
    vat : Optional[int]
    vat_enabled : Optional[bool]
    volume : Optional[int]
    weight : Optional[int]

    class Config:
        alias_generator = to_camel


class DocumentStateEntity(BaseModel):
    """Статусы можно добавлять, изменять и удалять через api. Поле color передается в АПИ как целое число 
    состоящее из 4х байт. Т.к. цвет передается в цветовом пространстве ARGB, каждый байт отвечает за свой 
    цвет соответственно: 1 - за прозрачность, 2 - за красный цвет, 3 - за зеленый, 4 - за синий. Каждый 
    байт принимает значения от 0 до 255 как и цвет в каждом из каналов цветового пространства. Получившееся 
    в итоге из 4 записанных последовательно байт число, переведенное в 10-чную систему счисления и 
    является представлением цвета статуса в JSON API."""
    account_id : UUID
    color : str
    entity_type : str
    id : UUID
    meta : Meta
    name : str
    state_type : Literal['Regular', 'Successful', 'Unsuccessful']

    class Config:
        alias_generator = to_camel


class SalesChannelEntity(BaseModel):
    """Кодом сущности для Канала продаж в составе JSON API является ключевое слово saleschannel."""
    account_id : UUID
    archived : bool
    code : Optional[str]
    description : Optional[str]
    external_code : str
    group : MetaArray
    id : UUID
    meta : Meta
    name : str
    owner : MetaArray
    shared : bool
    type : SalesChannelEnum
    updated : datetime

    class Config:
        alias_generator = to_camel


class CustomerOrderPositionEntity(BaseModel):
    """Model for a position in a customer order"""
    accountId : UUID
    assortment : MetaArray

class CustomerOrderEntity(BaseModel):
    """Model for a customer order, containts nested models for various entities from Moysklad"""
    account_id : Optional[UUID]
    agent : MetaArray           #Метаданные контрагента
    agent_account : Optional[MetaArray]        #Метаданные счета контрагента
    applicable : Optional[bool]       #Отметка о проведении
    attributes : Optional[list[Attribute]]
    code : Optional[str]
    contract : Optional[MetaArray]
    created : Optional[datetime]
    deleted : Optional[datetime]
    delivery_planned_moment : Optional[datetime]
    description : Optional[str]
    external_code : Optional[str]
    files : Optional[MetaArray]
    group : Optional[MetaArray]
    id : Optional[UUID]
    invoiced_sum : Optional[float]         #Сумма счетов покупателю
    meta : Optional[Meta]
    moment : str
    name : str
    organization : MetaArray
    organization_account : Optional[MetaArray]
    owner : Optional[MetaArray]
    payed_sum : Optional[float]            #Сумма входящих платежей по Заказу
    positions : Optional[MetaArray]
    printed : Optional[bool]
    project : Optional[MetaArray]
    published : Optional[bool]
    rate : Optional[RateMetaArray]     #Rate
    reserved_sum : Optional[float]         #Сумма товаров в резерве
    sales_channel : Optional[MetaArray]
    shared : Optional[bool]
    shipment_address : Optional[str]
    shipment_address_full : Optional[ActualAddressEntity]      #ShipmentAddressFull
    shipped_sum : Optional[float]              #Сумма отгруженного
    state : Optional[MetaArray]
    store : Optional[MetaArray]
    sum : Optional[int]           #Сумма Заказа в установленной валюте
    sync_id : Optional[UUID]
    tax_system : Optional[TaxSystemEnum]
    updated : Optional[datetime]
    vat_enabled : bool
    vat_included : Optional[bool]
    vat_sum : Optional[float]
    
    class Config:
        alias_generator = to_camel
        json_encoder = {
            # datetime: (lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'))
            datetime: (lambda dt: dt.isoformat(sep=' '))
        }