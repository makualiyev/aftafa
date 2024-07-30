from enum import Enum

from pydantic import BaseModel


class UomEnum(str, Enum):
    KGM = 'кг'
    LTR = 'л (дм3)'
    MTR = 'м'
    MTK = 'м2'
    MTQ = 'м3'
    TNE = 'т'
    NMP = 'упак'
    PCE = 'шт'


class NomenclatureTypeEnum(str, Enum):
    GOODS = 'Товар'
    JOB = 'Работа'
    SERVICE = 'Услуги'
    SET = 'Набор'


class VatTypeEnum(str, Enum):
    VAT_20 = '20%'
    VAT_20_120 = '20/120'
    VAT_10 = '10%'
    VAT_10_110 = '10/110'
    VAT_0 = '0%'
    NO_VAT = 'Без НДС'
    VAT_18 = '18%'
    VAT_18_118 = '18/118'


class LegalTypeEnum(str, Enum):
    INDIVIDUAL = 'Физическое лицо'
    LEGAL_ENTITY = 'Юридическое лицо'


class CurrencyEnum(str, Enum):
    RUB = 'руб.'
    USD = 'USD'
    EUR = 'EUR'


class InventoryRecordMovementTypeEnum(str, Enum):
    expense = 'expense'
    income = 'income'
    