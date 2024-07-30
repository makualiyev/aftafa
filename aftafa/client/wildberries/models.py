from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.dialects.postgresql import (
    UUID as pg_UUID,
    BIGINT
)
import sqlalchemy as sa

from aftafa.common.dal import postgres_url as db_url, engine as db_engine, session as db_session
from aftafa.client.wildberries.schemas import (
    DeliveryTypeEnum,
    OrderStatusEnum,
    OrderUserStatusEnum,
    CurrencyCodeEnum
)


Base = declarative_base()
engine = db_engine
session = db_session

class Supplier(Base):
    """Represents supplier a.k.a legal entity for a given account"""
    __tablename__ = 'supplier'
    __table_args__ = {"schema" : "wildberries"}

    uuid = sa.Column(pg_UUID, unique=True, nullable=False)
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False)


class Card(Base):
    """Represents a card from the main site. Contains one or more nomenclatures
    attached, and may contain some variations of those."""
    __tablename__ = 'card'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)                                                # imtID
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    
    updated_at = sa.Column(sa.DateTime, nullable=True)

    children = relationship("Nomenclature")


class Nomenclature(Base):
    """Represents a nomenclature attached to a specific card. On simpler terms
    it can be compared with offers on other mps (OZON, Yandex)"""
    __tablename__ = 'nomenclature'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False)                                                # nmID
    card_id = sa.Column(sa.Integer, sa.ForeignKey(Card.id, ondelete='CASCADE'), nullable=True)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)

    vendor_code = sa.Column(sa.String(155), nullable=False)
    object = sa.Column(sa.String(255), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    brand = sa.Column(sa.String(155), nullable=False)
    primary_image = sa.Column(sa.String(100), nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)

    children = relationship("Variation")

    
class NomenclatureDimension(Base):
    """Represents a nomenclature dimensions."""
    __tablename__ = 'nomenclature_dimension'
    __table_args__ = {'schema' : 'wildberries'}

    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), primary_key=True, unique=True, nullable=False)

    weight = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    length = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    width = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    depth = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    volume = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)


class Variation(Base):
    """Represents a variation attached to a specific nomenclature. Usually rep-
    resents a variety of sizes of clothes or some other unique property of goods."""
    __tablename__ = 'variation'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)                                                # chrtID
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)

    alt_id = sa.Column(sa.String(length=55), unique=True, nullable=False)                            # alternative id (`wb_id` in local reports) as a concatenation of Nomenclature id + tech size
    barcode = sa.Column(sa.String(100), nullable=True)
    tech_size = sa.Column(sa.String(25), nullable=False, default='0')
    wb_size = sa.Column(sa.String(25), nullable=True)


class NomenclaturePrice(Base):
    """Prices for nomenclatures with given percent of discount and promocode."""
    __tablename__ = 'nm_price'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), primary_key=True, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    discount = sa.Column(sa.Integer, nullable=False, default=0)
    promocode = sa.Column(sa.Integer, nullable=False, default=0)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class Warehouse(Base):
    """Warehouse information fetched from new API, kind of a supplier's virtual WHs."""
    __tablename__ = 'warehouse'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String(200), nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id), nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)


class StocksOnWarehouses(Base):
    """Warehouse information fetched from new API, kind of a supplier's virtual WHs."""
    __tablename__ = 'stocks_on_warehouses'
    __table_args__ = (
            sa.UniqueConstraint(
                'variation_id',
                'warehouse_id',
                'updated_at'
            ),
            {
            "schema": 'wildberries',
        },
        )

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouse.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    barcode = sa.Column(sa.String(100), nullable=True)
    amount = sa.Column(sa.Integer, nullable=False)

    updated_at = sa.Column(sa.Date, nullable=False)



class Supply(Base):
    """Supplies to the warehouse that consist of FBS postings"""
    __tablename__ = 'supply'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.String(55), primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    name = sa.Column(sa.String(155), nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)
    closed_at = sa.Column(sa.DateTime, nullable=True)
    scan_dt = sa.Column(sa.DateTime, nullable=True)
    is_large_cargo = sa.Column(sa.Boolean, nullable=True)
    done = sa.Column(sa.Boolean, nullable=True)


class Order(Base):
    """Order information fetched from new API."""
    __tablename__ = 'order'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    supply_id = sa.Column(sa.String(55), sa.ForeignKey(Supply.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouse.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    rid = sa.Column(sa.String(55), unique=True, index=True, nullable=False)
    order_uid = sa.Column(sa.String(155), nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)
    vendor_code = sa.Column(sa.String(155), nullable=False)
    barcode = sa.Column(sa.String(55), nullable=True)
    price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    converted_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    currency_code = sa.Column(sa.String(15), nullable=False)
    converted_currency_code = sa.Column(sa.String(15), nullable=False)
    is_large_cargo = sa.Column(sa.Boolean, nullable=False)
    delivery_type = sa.Column(sa.String(10), nullable=False)
    cargo_type = sa.Column(sa.Integer, nullable=True)

    has_sticker = sa.Column(sa.Boolean, nullable=False)


class OrderSticker(Base):
    """Order information fetched from new API."""
    __tablename__ = 'order_sticker'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    order_id = sa.Column(sa.BigInteger, sa.ForeignKey(Order.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    part_a = sa.Column(sa.Integer, nullable=False)
    part_b = sa.Column(sa.Integer, nullable=False)
    barcode = sa.Column(sa.String(155), nullable=False)



# class OrderBarcode(Base):
#     """Order barcodes as a list"""
#     __tablename__ = 'order_barcodes'
#     __table_args__ = {'schema' : 'wildberries'}

#     id = sa.Column(sa.Integer, primary_key=True)
#     order_id = sa.Column(sa.String(32), sa.ForeignKey(Order.id, ondelete='CASCADE'), nullable=False)
#     barcode = sa.Column(sa.String(55), nullable=False)
    
    
# class OrderUserInfo(Base):
#     """Order information fetched from new API."""
#     __tablename__ = 'order_user_info'
#     __table_args__ = {'schema' : 'wildberries'}

#     order_id = sa.Column(sa.String(32), sa.ForeignKey(Order.id, ondelete='CASCADE'), primary_key=True, nullable=False)
#     fio = sa.Column(sa.String(255), nullable=True)
#     email = sa.Column(sa.String(255), nullable=True)
#     phone = sa.Column(sa.String(255), nullable=True)


# class OrderDeliveryAddressDetails(Base):
#     """Order information fetched from new API."""
#     __tablename__ = 'order_delivery_details'
#     __table_args__ = {'schema' : 'wildberries'}

#     order_id = sa.Column(sa.String(32), sa.ForeignKey(Order.id, ondelete='CASCADE'), primary_key=True, nullable=False)
#     province = sa.Column(sa.String(255), nullable=True)                                         # FIXME deleted
#     area = sa.Column(sa.String(255), nullable=True)
#     city = sa.Column(sa.String(255), nullable=True)
#     street = sa.Column(sa.String(255), nullable=True)
#     home = sa.Column(sa.String(255), nullable=True)
#     flat = sa.Column(sa.String(255), nullable=True)
#     entrance = sa.Column(sa.String(255), nullable=True)


class SupplyWarehouse(Base):
    """Warehouse information fetched from stocks and orders / sales from statistics API."""
    __tablename__ = 'supply_warehouse'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False)
    name = sa.Column(sa.String(100), nullable=False)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())

# class SupplyIncome(Base):
#     """Supply incomes from stats Wildberries"""
#     __tablename__ = 'supply_income'
#     __table_args__ = {'schema' : 'wildberries'}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), primary_key=True, nullable=False)
#     price = sa.Column(sa.Integer, nullable=False)
#     discount = sa.Column(sa.Integer, nullable=False, default=0)
#     promocode = sa.Column(sa.Integer, nullable=False, default=0)
#     updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class SupplyStock(Base):
    """Supply stocks from stats Wildberries"""
    __tablename__ = 'supply_stock'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), primary_key=True, nullable=False)
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    is_supply = sa.Column(sa.Boolean, nullable=False)
    is_realization = sa.Column(sa.Boolean, nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(SupplyWarehouse.id), nullable=False)
    warehouse = sa.Column(sa.String(100), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False, default=0)
    qunatity_full = sa.Column(sa.Integer, nullable=False, default=0)
    qunatity_not_in_orders = sa.Column(sa.Integer, nullable=False, default=0)
    in_way_to_client = sa.Column(sa.Integer, nullable=False, default=0)
    in_way_from_client = sa.Column(sa.Integer, nullable=False, default=0)
    days_on_site = sa.Column(sa.Integer, nullable=False)
    brand = sa.Column(sa.String(100), nullable=False)
    sc_code = sa.Column(sa.String(50), nullable=False)
    last_change_date = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class BackSupplyStock(Base):
    """Supply stocks directly from site Wildberries"""
    __tablename__ = 'back_supply_stock'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(SupplyWarehouse.id), nullable=True)
    warehouse = sa.Column(sa.String(100), nullable=False)

    barcode = sa.Column(sa.String(30), nullable=True)
    supplier_article = sa.Column(sa.String(75), nullable=True)
    quantity_in_transit = sa.Column(sa.Integer, nullable=False, default=0)
    quantity_for_sale = sa.Column(sa.Integer, nullable=False, default=0)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class SupplyOrder(Base):
    """Supply orders from stats Wildberries"""
    __tablename__ = 'supply_order'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.String(50), primary_key=True, unique=True, nullable=False)         #gNumber from response model
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    order_date = sa.Column(sa.Date, nullable=False)


class SupplyOrderPosition(Base):
    """Supply order's positions from stats Wildberries"""
    __tablename__ = 'supply_order_position'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(BIGINT, primary_key=True, unique=True, nullable=False)         #odid from response model
    order_id = sa.Column(sa.String(50), sa.ForeignKey(SupplyOrder.id, ondelete='CASCADE'), nullable=False)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    srid = sa.Column(sa.String(50), nullable=True, unique=True, index=True)
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(SupplyWarehouse.id), nullable=True)
    warehouse = sa.Column(sa.String(100), nullable=False)
    region = sa.Column(sa.String(200), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=False, default=1)
    total_price = sa.Column(sa.Integer, nullable=False)
    discount_percent = sa.Column(sa.Integer, nullable=False, default=0)
    sticker = sa.Column(sa.String(50), nullable=True)
    income_id = sa.Column(sa.Integer, nullable=True)                   #income of goods (supply income)
    is_cancel = sa.Column(sa.Boolean, nullable=False, default=False)
    cancel_date = sa.Column(sa.Date, nullable=True)
    last_change_date = sa.Column(sa.Date, nullable=False)
    

class SupplyOrderV2(Base):
    """Supply order's positions from stats Wildberries"""
    __tablename__ = 'supply_order_v2'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(BIGINT, primary_key=True, autoincrement=True)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    srid = sa.Column(sa.String(50), nullable=False, unique=True, index=True)
    order_type = sa.Column(sa.String(250), nullable=True)
    g_number = sa.Column(sa.String(50), nullable=True)
    sticker = sa.Column(sa.String(50), nullable=True)
    # -------------------------------------------------------------------------
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    # -------------------------------------------------------------------------
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    category = sa.Column(sa.String(50), nullable=True)
    subject = sa.Column(sa.String(50), nullable=True)
    brand = sa.Column(sa.String(50), nullable=True)
    # -------------------------------------------------------------------------
    warehouse_name = sa.Column(sa.String(100), nullable=False)
    country_name = sa.Column(sa.String(200), nullable=True)
    region_name = sa.Column(sa.String(200), nullable=True)
    oblast_okrug_name = sa.Column(sa.String(200), nullable=True)
    # -------------------------------------------------------------------------
    income_ID = sa.Column(sa.Integer, nullable=True)                   #income of goods (supply income)
    is_supply = sa.Column(sa.Boolean, nullable=False, default=False)
    is_realization = sa.Column(sa.Boolean, nullable=False, default=False)
    is_cancel = sa.Column(sa.Boolean, nullable=False, default=False)
    cancel_date = sa.Column(sa.Date, nullable=True)
    # -------------------------------------------------------------------------
    quantity = sa.Column(sa.Integer, nullable=False, default=1)
    total_price = sa.Column(sa.Integer, nullable=False)
    discount_percent = sa.Column(sa.Integer, nullable=False, default=0)
    spp = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    finished_price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    price_with_disc = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    # -------------------------------------------------------------------------
    last_change_date = sa.Column(sa.Date, nullable=False)
    date = sa.Column(sa.Date, nullable=False)


class SupplySaleV2(Base):
    """Supply order's positions from stats Wildberries"""
    __tablename__ = 'supply_sale_v2'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(BIGINT, primary_key=True, autoincrement=True)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    sale_ID = sa.Column(sa.String(15), nullable=False, unique=True, index=True)
    srid = sa.Column(sa.String(50), nullable=False, index=True)
    g_number = sa.Column(sa.String(50), nullable=True)
    sticker = sa.Column(sa.String(50), nullable=True)
    # -------------------------------------------------------------------------
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    # -------------------------------------------------------------------------
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    category = sa.Column(sa.String(50), nullable=True)
    subject = sa.Column(sa.String(50), nullable=True)
    brand = sa.Column(sa.String(50), nullable=True)
    # -------------------------------------------------------------------------
    warehouse_name = sa.Column(sa.String(100), nullable=False)
    country_name = sa.Column(sa.String(200), nullable=True)
    region_name = sa.Column(sa.String(200), nullable=True)
    oblast_okrug_name = sa.Column(sa.String(200), nullable=True)
    # -------------------------------------------------------------------------
    income_ID = sa.Column(sa.Integer, nullable=True)                   #income of goods (supply income)
    is_supply = sa.Column(sa.Boolean, nullable=False, default=False)
    is_realization = sa.Column(sa.Boolean, nullable=False, default=False)
    is_storno = sa.Column(sa.Boolean, nullable=False, default=False)
    # -------------------------------------------------------------------------
    total_price = sa.Column(sa.Integer, nullable=False)
    discount_percent = sa.Column(sa.Integer, nullable=False, default=0)
    spp = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    finished_price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    price_with_disc = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    for_pay = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    # -------------------------------------------------------------------------
    last_change_date = sa.Column(sa.Date, nullable=False)
    date = sa.Column(sa.Date, nullable=False)


class SupplyStockV2(Base):
    """Supply order's positions from stats Wildberries"""
    __tablename__ = 'supply_stock_v2'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(BIGINT, primary_key=True, autoincrement=True)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    # -------------------------------------------------------------------------
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    # -------------------------------------------------------------------------
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    category = sa.Column(sa.String(50), nullable=True)
    subject = sa.Column(sa.String(50), nullable=True)
    brand = sa.Column(sa.String(50), nullable=True)
    # -------------------------------------------------------------------------
    warehouse_name = sa.Column(sa.String(100), nullable=False)
    sc_code = sa.Column(sa.String(50), nullable=False)
    # -------------------------------------------------------------------------
    
    is_supply = sa.Column(sa.Boolean, nullable=False, default=False)
    is_realization = sa.Column(sa.Boolean, nullable=False, default=False)
    
    # -------------------------------------------------------------------------
    quantity = sa.Column(sa.Integer, nullable=False)
    in_way_to_client = sa.Column(sa.Integer, nullable=False)
    in_way_from_client = sa.Column(sa.Integer, nullable=False)
    quantity_full = sa.Column(sa.Integer, nullable=False)
    price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    discount = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    # -------------------------------------------------------------------------
    last_change_date = sa.Column(sa.DateTime, nullable=False)
    extracted_at = sa.Column(sa.DateTime, nullable=False)


class SupplySale(Base):
    """Supply sales from stats Wildberries"""
    __tablename__ = 'supply_sale'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.String(length=15), primary_key=True, nullable=False)          # saleID
    order_id = sa.Column(sa.String(50), sa.ForeignKey(SupplyOrder.id, ondelete='CASCADE'), nullable=False)
    order_pos_id = sa.Column(BIGINT, sa.ForeignKey(SupplyOrderPosition.id, ondelete='CASCADE'), nullable=False)      # odid
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    srid = sa.Column(sa.String(50), sa.ForeignKey(SupplyOrderPosition.srid, ondelete='CASCADE'), nullable=True)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(SupplyWarehouse.id), nullable=True)

    date = sa.Column(sa.DateTime, nullable=False)
    last_change_date = sa.Column(sa.DateTime, nullable=False)
    supplier_article = sa.Column(sa.String(75), nullable=False)
    tech_size = sa.Column(sa.String(75), nullable=False)
    barcode = sa.Column(sa.String(30), nullable=False)
    total_price = sa.Column(sa.Integer, nullable=False)
    discount_percent = sa.Column(sa.Integer, nullable=False, default=0)
    finished_price = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    price_with_disc = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)
    for_pay = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0.0)

    income_id = sa.Column(sa.Integer, nullable=True)                   #income of goods (supply income)
    is_supply = sa.Column(sa.Boolean, nullable=False)
    is_realization = sa.Column(sa.Boolean, nullable=False)
    is_storno = sa.Column(sa.Integer, nullable=False, default=0)
    promo_code_discount = sa.Column(sa.Integer, nullable=False)
    spp = sa.Column(sa.Integer, nullable=False)
    sticker = sa.Column(sa.String(50), nullable=True)
    warehouse = sa.Column(sa.String(50), nullable=False)
    country = sa.Column(sa.String(200), nullable=False)
    region = sa.Column(sa.String(200), nullable=True)

# realizationreport_id: int                               # Номер отчета
#     suppliercontract_code: Optional[int]                    # Договор
#     rid: int                                                # Уникальный идентификатор позиции заказа
#     rr_dt: str                                              # Дата операции. Присылается с явным указанием часового пояса.
#     rrd_id: int                                             # Номер строки
#     gi_id: int                                              # Номер поставки
#     subject_name: Optional[str]                             # Предмет
#     nm_id: Optional[int]                                    # Артикул
#     brand_name: Optional[str]                               # Бренд
#     sa_name: Optional[str]                                  # Артикул поставщика
#     ts_name: Optional[str]                                  # Размер
#     barcode: Optional[str]                                  # Бар-код
#     doc_type_name: str                                      # Enum: "Продажа" "Возврат" Тип документа
#     quantity: int                                           # Количество
#     retail_price: float                                     # Цена розничная
#     retail_amount: float                                    # Сумма продаж (возвратов)
#     sale_percent: int                                       # Согласованная скидка
#     commission_percent: float                               # Процент комиссии
#     office_name: Optional[str]                              # Склад
#     supplier_oper_name: str                                 # Обоснование для оплаты
#     order_dt: str                                           # Дата заказа. Присылается с явным указанием часового пояса.
#     sale_dt: str                                            # Дата продажи. Присылается с явным указанием часового пояса.
#     shk_id: int                                             # Штрих-код
#     retail_price_withdisc_rub: float                        # Цена розничная с учетом согласованной скидки
#     delivery_amount: int                                    # Количество доставок
#     return_amount: int                                      # Количество возвратов
#     delivery_rub: float                                     # Стоимость логистики
#     gi_box_type_name: str                                   # Тип коробов
#     product_discount_for_report: float                      # Согласованный продуктовый дисконт
#     supplier_promo: float                                   # Промокод
#     ppvz_spp_prc: float                                     # Скидка постоянного покупателя
#     ppvz_kvw_prc_base: float                                # Размер кВВ без НДС, % базовый
#     ppvz_kvw_prc: float                                     # Итоговый кВВ без НДС, %
#     ppvz_sales_commission: float                            # Вознаграждение с продаж до вычета услуг поверенного, без НДС
#     ppvz_for_pay: float                                     # К перечислению продавцу за реализованный товар
#     ppvz_reward: float                                      # Возмещение расходов услуг поверенного
#     ppvz_vw: float                                          # Вознаграждение WB без НДС
#     ppvz_vw_nds: float                                      # НДС с вознаграждения WB
#     ppvz_office_id: int                                     # Номер офиса
#     ppvz_office_name: Optional[str]                                   # Наименование офиса доставки
#     ppvz_supplier_id: int                                   # Номер партнера
#     ppvz_supplier_name: str                                 # Партнер
#     ppvz_inn: str                                           # ИНН партнера
#     declaration_number: str                                 # Номер таможенной декларации
#     sticker_id: Optional[str]                                         # Цифровое значение стикера, который клеится на товар в процессе сборки заказа по системе Маркетплейс.
#     site_country: str                                       # Страна продажи
#     penalty: float                                          # Штрафы
#     additional_payment: float                               # Доплаты
#     bonus_type_name: Optional[str]                                    # Обоснование штрафов и доплат
#     srid: str                                               # Уникальный идентификатор заказа, функционально аналогичный odid/rid. 
class SupplyFinReport(Base):
    """Supply sales from stats Wildberries"""
    __tablename__ = 'supply_fin_report'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False)          # rrd_id
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    realizationreport_id = sa.Column(sa.Integer, index=True, nullable=False)
    srid = sa.Column(sa.String(50), index=True, nullable=False)
    rid = sa.Column(sa.String(50), index=True, nullable=True)
    date_from = sa.Column(sa.Date, nullable=False)
    date_to = sa.Column(sa.Date, nullable=False)
    rr_dt = sa.Column(sa.Date, nullable=True)
    create_dt = sa.Column(sa.DateTime, nullable=False)
    suppliercontract_code = sa.Column(sa.Integer, nullable=True)
    gi_id = sa.Column(sa.Integer, nullable=False, default=0)

    doc_type_name = sa.Column(sa.String(75), nullable=False)
    supplier_oper_name = sa.Column(sa.String(75), nullable=False)
    office_name = sa.Column(sa.String(75), nullable=True)
    site_country = sa.Column(sa.String(25), nullable=True)
    acquiring_bank = sa.Column(sa.String(75), nullable=True)

    order_dt = sa.Column(sa.Date, nullable=True)
    sale_dt = sa.Column(sa.Date, nullable=True)
    shk_id = sa.Column(sa.BigInteger, nullable=True)
    sticker_id = sa.Column(sa.String(75), nullable=True)
    gi_box_type_name = sa.Column(sa.String(25), nullable=False)

    subject_name = sa.Column(sa.String(100), nullable=True)
    nm_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=True)
    brand_name = sa.Column(sa.String(75), nullable=True)
    sa_name = sa.Column(sa.String(75), nullable=True)
    ts_name = sa.Column(sa.String(25), nullable=True)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=True)
    barcode = sa.Column(sa.String(75), nullable=True)
    declaration_number = sa.Column(sa.String(75), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=True)
    retail_price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    retail_amount = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    sale_percent = sa.Column(sa.Integer, nullable=True)
    commission_percent = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    retail_price_withdisc_rub = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    delivery_amount = sa.Column(sa.Integer, nullable=True)
    return_amount = sa.Column(sa.Integer, nullable=True)
    delivery_rub = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_discount_for_report = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    supplier_promo = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    penalty = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    additional_payment = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    bonus_type_name = sa.Column(sa.String(75), nullable=True)
    acquiring_fee = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    rebill_logistic_cost = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    rebill_logistic_org = sa.Column(sa.String(255), nullable=True)

    ppvz_spp_prc = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_kvw_prc_base = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_kvw_prc = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    sup_rating_prc_up = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    is_kgvp_v2 = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_sales_commission = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_for_pay = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_reward = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_vw = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_vw_nds = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    ppvz_office_id = sa.Column(sa.BigInteger, nullable=True)
    ppvz_office_name = sa.Column(sa.String(75), nullable=True)
    ppvz_supplier_id = sa.Column(sa.Integer, nullable=True)
    ppvz_supplier_name = sa.Column(sa.String(75), nullable=True)
    ppvz_inn = sa.Column(sa.String(25), nullable=True)

    currency_name = sa.Column(sa.String(55), nullable=True)
    kiz = sa.Column(sa.String(255), nullable=True)


class NomenclaturePriceV2(Base):
    """Prices for nomenclatures with given percent of discount and promocode."""
    __tablename__ = 'nm_price_v2'
    __table_args__ = {'schema' : 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nomenclature_id = sa.Column(sa.Integer, sa.ForeignKey(Nomenclature.id, ondelete='CASCADE'), nullable=False)
    variation_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE'), nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    vendor_code = sa.Column(sa.String(155), nullable=False)
    tech_size_name = sa.Column(sa.String(25), nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    discount = sa.Column(sa.Integer, nullable=False)
    discounted_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    currency_code = sa.Column(sa.String(25), nullable=False)
    editable_size_price = sa.Column(sa.Boolean, nullable=False)

    report_date = sa.Column(sa.Date, nullable=False)
    extracted_at = sa.Column(sa.DateTime, nullable=False)


# class BackPromo(Base):
#     """Supply sales from stats Wildberries"""
#     __tablename__ = 'back_promo'
#     __table_args__ = {'schema': 'wildberries'}


    # banner_url: "http://service.store-keeper.svc.k8s.datapro/api/v1/files//data"
    # date_from: "2022-11-02T13:00:00Z"
    # date_to: "2022-11-14T20:59:59Z"
    # description: "Присоединяйтесь к самому главному событию года:  Всемирному дню шопинга.\nМы уменьшим свою комиссию на товары-участники на 8% за небольшое снижение цены (комиссия при этом составит не менее 3%).\nВсе узнают о нашей распродаже: мы подготовили Тв-рекламу на топовых каналах, Наружную рекламу на билбордах.\nТовары, участвующие в акции, в дни распродажи будут подняты в самой востребованной сортировке «По популярности» вверх, чтобы наши клиенты имели доступ к самым выгодным товарам в дни акции, а Вы получили еще больше продаж и отзывов. Чем выгоднее Вы дадите предложение, тем больше шанс быть на первых позициях. \nТрадиционно мы так же оформим в акции: \n-большие баннеры с товарами распродажи на самых топовых местах, \n-Яркие плашки на товарах -участниках привлекут внимание в каталоге \n- и конечно пуши, смс-рассылки и уведомления нашим покупателям"
    # discount_max: 0
    # discount_min: 0
    # erp_id: null
    # id: 852
    # is_bonus_promo: false
    # is_draft: false
    # is_erp: false
    # is_promo: false
    # is_special: false
    # period_id: 266
    # promo_max: 0
    # promo_min: 0
    # promo_name: "Всемирный День Шопинга: комиссия -8"
    # title: "САМАЯ БОЛЬШАЯ РАСПРОДАЖА 2022!"


class LocalMapping(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'local_mapping'
    __table_args__ = {'schema': 'wildberries'}

    wb_chrt_id = sa.Column(sa.Integer, sa.ForeignKey(Variation.id, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, unique=True, nullable=False)
    sku_id = sa.Column(sa.String(155), sa.ForeignKey('staging_local.general_skus.sku_id', ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=True)
    note = sa.Column(sa.String(55), nullable=True)


class WebSeller(Base):
    __tablename__ = 'web_seller'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(125), nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class WebCatalogProduct(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'web_catalog_product'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    meta_seller_id = sa.Column(sa.String(255), nullable=False)
    meta_state = sa.Column(sa.String(255), nullable=False)
    meta_version = sa.Column(sa.String(255), nullable=False)
    meta_payload_version = sa.Column(sa.String(255), nullable=False)
    meta_report_date = sa.Column(sa.String(100), nullable=False)

    sort_ = sa.Column(sa.String(255), nullable=True)
    ksort = sa.Column(sa.String(255), nullable=True)
    time1 = sa.Column(sa.String(255), nullable=True)
    time2 = sa.Column(sa.String(255), nullable=True)
    wh = sa.Column(sa.String(255), nullable=True)
    dtype = sa.Column(sa.String(255), nullable=True)
    dist = sa.Column(sa.String(255), nullable=True)
    id_ = sa.Column(sa.String(255), nullable=False)
    root = sa.Column(sa.String(255), nullable=True)
    kind_id = sa.Column(sa.String(255), nullable=True)
    brand = sa.Column(sa.String(255), nullable=True)
    brand_id = sa.Column(sa.String(255), nullable=True)
    site_brand_id = sa.Column(sa.String(255), nullable=True)
    subject_id = sa.Column(sa.String(255), nullable=True)
    subject_parent_id = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    supplier = sa.Column(sa.String(255), nullable=True)
    supplier_id = sa.Column(sa.String(255), nullable=True)
    supplier_rating = sa.Column(sa.String(255), nullable=True)
    supplier_flags = sa.Column(sa.String(255), nullable=True)
    pics = sa.Column(sa.String(255), nullable=True)
    rating = sa.Column(sa.String(255), nullable=True)
    review_rating = sa.Column(sa.String(255), nullable=True)
    feedbacks = sa.Column(sa.String(255), nullable=True)
    panel_promo_id = sa.Column(sa.String(255), nullable=True)
    promo_text_card = sa.Column(sa.String(255), nullable=True)
    promo_text_cat = sa.Column(sa.String(255), nullable=True)
    volume = sa.Column(sa.String(255), nullable=True)
    view_flags = sa.Column(sa.String(255), nullable=True)
    total_quantity = sa.Column(sa.String(255), nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=False)
    

class WebCatalogProductColor(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'web_catalog_product_color'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    web_catalog_product_id = sa.Column(sa.Integer, sa.ForeignKey(WebCatalogProduct.id), index=True, nullable=False)

    color_id = sa.Column(sa.Integer)
    color_name = sa.Column(sa.String(100))
    

class WebCatalogProductSize(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'web_catalog_product_size'
    __table_args__ = {'schema': 'wildberries'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    web_catalog_product_id = sa.Column(sa.Integer, sa.ForeignKey(WebCatalogProduct.id), index=True, nullable=False)

    name = sa.Column(sa.String(255), nullable=True)
    orig_name = sa.Column(sa.String(255), nullable=True)
    rank = sa.Column(sa.String(255), nullable=True)
    option_id = sa.Column(sa.String(255), nullable=True)
    wh = sa.Column(sa.String(255), nullable=True)
    dtype = sa.Column(sa.String(255), nullable=True)
    sale_conditions = sa.Column(sa.String(255), nullable=True)
    payload = sa.Column(sa.String(255), nullable=True)

    price_basic = sa.Column(sa.String(255), nullable=True)
    price_product = sa.Column(sa.String(255), nullable=True)
    price_total = sa.Column(sa.String(255), nullable=True)
    price_logistics = sa.Column(sa.String(255), nullable=True)
    price_return_ =sa.Column(sa.String(255), nullable=True)
    
    extracted_at = sa.Column(sa.DateTime, nullable=False)

