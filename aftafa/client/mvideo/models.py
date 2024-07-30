from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import (
    UUID as pg_UUID
)
import sqlalchemy as sa

from aftafa.common.dal import postgres_url as db_url
from aftafa.client.mvideo.schemas import (
    LifeCycleStatusEnum,
    OrderStatusEnum
)


Base = declarative_base()
engine = sa.create_engine(db_url)
session = Session(engine)

class Supplier(Base):
    """Represents supplier a.k.a legal entity for a given account"""
    __tablename__ = 'supplier'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.String(55), primary_key=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False)
    slug = sa.Column(sa.String(55), nullable=False)


class Brand(Base):
    """
    """
    __tablename__ = 'brand'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String(100), nullable=False)


class Group(Base):
    """
    """
    __tablename__ = 'group'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False)
    name = sa.Column(sa.String(200), nullable=False)


class Product(Base):
    """Represents a product from the main site. Contains one or more nomenclatures
    attached, and may contain some variations of those."""
    __tablename__ = 'product'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    supplier_code = sa.Column(sa.String(55), sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    material_number = sa.Column(sa.BigInteger, unique=True, index=True, nullable=False)                                                 # Mvideo SAP code
    sap_code_eldorado = sa.Column(sa.BigInteger, unique=True, nullable=True)                                                           # Eldorado CODE
    group_id = sa.Column(sa.BigInteger, sa.ForeignKey(Group.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    brand_id = sa.Column(sa.Integer, sa.ForeignKey(Brand.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    
    name = sa.Column(sa.String(255), nullable=True)
    material_model_name = sa.Column(sa.String(155), nullable=True)                                                                      # materialModelName
    supplier_material_number = sa.Column(sa.String(155), nullable=True)                                                                 # supplierMaterialNumber
    manufacturer_code = sa.Column(sa.String(155), nullable=True)                                                               # manufacturerCode
    material_account_name = sa.Column(sa.String(155), nullable=True)                                                                    # ucetnoe naimenovanie
    retail_network_mvideo = sa.Column(sa.Boolean, nullable=False)
    retail_network_eldorado = sa.Column(sa.Boolean, nullable=False)
    product_type = sa.Column(sa.String(100), nullable=False)
    life_cycle_status = sa.Column(sa.Enum(LifeCycleStatusEnum), nullable=False)
    created_date = sa.Column(sa.DateTime, nullable=False)
    main_image = sa.Column(sa.String(155), nullable=True)
    unit = sa.Column(sa.String(100), nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False)
    review_status = sa.Column(sa.String(100), nullable=True)


class ProductPrice(Base):
    """
    represents price information from MVM
    """
    __tablename__ = 'product_price'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    price_uuid = sa.Column(pg_UUID, nullable=False)
    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)                                                 # Mvideo SAP code

    price_type = sa.Column(sa.String(100), nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    promo_price = sa.Column(sa.Integer, nullable=True)
    market_price = sa.Column(sa.Integer, nullable=True)
    currency = sa.Column(sa.String(25), nullable=False)
    date_start = sa.Column(sa.Date, nullable=True)
    date_end = sa.Column(sa.Date, nullable=True)

    export_status = sa.Column(sa.String(55), nullable=False)
    approval_status = sa.Column(sa.String(55), nullable=False)
    market_price_status = sa.Column(sa.String(55), nullable=False)


class ProductStock(Base):
    """
    represents price information from MVM
    """
    __tablename__ = 'product_stock'
    __table_args__ = (
            sa.UniqueConstraint(
                'material_number',
                'warehouse_code',
                'updated_at'
            ),
            {
            "schema": 'mvm',
        },
        )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)                                                 # Mvideo SAP code
    warehouse_code = sa.Column(sa.String(10), nullable=False)

    quantity = sa.Column(sa.Integer, nullable=False)
    reserved = sa.Column(sa.Integer, nullable=False)
    available = sa.Column(sa.Integer, nullable=False)
    date_start = sa.Column(sa.Date, nullable=True)
    date_end = sa.Column(sa.Date, nullable=True)
    unit = sa.Column(sa.String(55), nullable=False)

    updated_at = sa.Column(sa.Date, nullable=False)


class Order(Base):
    """
    """
    __tablename__ = 'order'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    order_uuid = sa.Column(pg_UUID, nullable=False)
    supplier_code = sa.Column(sa.String(55), sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    order_number = sa.Column(sa.String(25), unique=True, index=True, nullable=False)

    consignment = sa.Column(sa.String(25), nullable=False)
    delivery_location = sa.Column(sa.String(15), nullable=False)
    date_create = sa.Column(sa.Date, nullable=False)
    delivery_date = sa.Column(sa.Date, nullable=False)
    type_of_sale = sa.Column(sa.String(15), nullable=False)
    status = sa.Column(sa.String(100), nullable=False)
    currency = sa.Column(sa.String(15), nullable=True)
    last_import_date = sa.Column(sa.DateTime, nullable=True)
    payment_terms = sa.Column(sa.String(100), nullable=True)
    total_entry = sa.Column(sa.Integer, nullable=True)
    total_tax = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    version = sa.Column(sa.Integer, nullable=True)


class OrderEntry(Base):
    """
    """
    __tablename__ = 'order_entry'
    __table_args__ = (
            sa.UniqueConstraint(
                'order_number',
                'material_supplier_code'
            ),
            {
            "schema": 'mvm',
        },
        )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    order_entry_uuid = sa.Column(pg_UUID, unique=True, nullable=False)
    order_number = sa.Column(sa.String(55), sa.ForeignKey(Order.order_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    material_supplier_code = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    group_code = sa.Column(sa.BigInteger, nullable=False)
    material_code = sa.Column(sa.String(25), nullable=False)
    material_name = sa.Column(sa.String(100), nullable=False)
    gross_weight = sa.Column(sa.Integer, nullable=False)
    package_volume = sa.Column(sa.Integer, nullable=False)
    purchase_price = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    purchase_sum = sa.Column(sa.Integer, nullable=False)
    
    assignment = sa.Column(sa.String(100), nullable=True)
    delivery_date = sa.Column(sa.String(100), nullable=True)
    delivery_location = sa.Column(sa.String(100), nullable=True)
    ean = sa.Column(sa.String(100), nullable=True)
    last_import_date = sa.Column(sa.String(100), nullable=True)
    net_weight = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    status = sa.Column(sa.String(100), nullable=True)
    tax = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    unit = sa.Column(sa.String(25), nullable=True)
    unit_volume = sa.Column(sa.String(25), nullable=True)
    vat_rate = sa.Column(sa.String(55), nullable=True)
    version = sa.Column(sa.Integer, nullable=True)
    weight_unit = sa.Column(sa.String(25), nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)


class ProductMovement(Base):
    """
    """
    __tablename__ = 'product_movement'
    __table_args__ = {"schema": "mvm"}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    product_movement_uuid = sa.Column(pg_UUID, unique=True, nullable=False)                                                                             #uid
    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)          #zmaterial

    product_type = sa.Column(sa.String(100), nullable=False)
    material_name = sa.Column(sa.String(100), nullable=False)
    state = sa.Column(sa.String(25), nullable=False)
    status = sa.Column(sa.String(25), nullable=False)
    object_number = sa.Column(sa.String(25), nullable=False)                                                                                            #zplant
    object_type = sa.Column(sa.String(55), nullable=False)
    city = sa.Column(sa.String(155), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    brand = sa.Column(sa.String(100), nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, default=func.now())


class MailListSales(Base):
    """
    """
    __tablename__ = 'mail_list_sales'
    __table_args__ = {'schema': 'mvm'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)          #zmaterial
    supplier_code = sa.Column(sa.String(55), sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    report_date = sa.Column(sa.Date, nullable=False)

    business_unit = sa.Column(sa.String(100), nullable=True)
    category = sa.Column(sa.String(100), nullable=True)
    plan_name = sa.Column(sa.String(100), nullable=True)
    group = sa.Column(sa.String(100), nullable=True)
    sale_technology = sa.Column(sa.String(100), nullable=True)

    price_up_to_date = sa.Column(sa.Integer, nullable=True)
    fit_stock = sa.Column(sa.Integer, nullable=True)
    overall_stock = sa.Column(sa.Integer, nullable=True)
    sold_qty = sa.Column(sa.Integer, nullable=True)
    sold_sum = sa.Column(sa.Integer, nullable=True)


class MailListStocks(Base):
    """
    """
    __tablename__ = 'mail_list_stocks'
    __table_args__ = {'schema': 'mvm'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)          #zmaterial
    supplier_code = sa.Column(sa.String(55), sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    report_date = sa.Column(sa.Date, nullable=False)

    object_number = sa.Column(sa.String(15), nullable=True)
    city = sa.Column(sa.String(100), nullable=True)
    object_type = sa.Column(sa.String(100), nullable=True)
    object_division = sa.Column(sa.String(15), nullable=True)
    storage_type = sa.Column(sa.String(200), nullable=True)
    material_name = sa.Column(sa.String(100), nullable=True)
    product_type = sa.Column(sa.String(100), nullable=True)
    material_brand = sa.Column(sa.String(15), nullable=True)

    fit_stock = sa.Column(sa.Integer, nullable=False, default=0)
    overall_stock = sa.Column(sa.Integer, nullable=False, default=0)

    fit_stock_in_rub = sa.Column(sa.Integer, nullable=True, default=0)
    reserved_stock = sa.Column(sa.Integer, nullable=True, default=0)
    reserved_stock_in_rub = sa.Column(sa.Integer, nullable=True, default=0)
    overall_stock_in_rub = sa.Column(sa.Integer, nullable=True, default=0)

    
# class ProductPriceChangeHistory(Base):
#     """
#     represents price information from MVM
#     """
#     __tablename__ = 'product_price'
#     __table_args__ = {"schema": "mvm"}
class LocalMapping(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'local_mapping'
    __table_args__ = {'schema': 'mvm'}

    material_number = sa.Column(sa.BigInteger, sa.ForeignKey(Product.material_number, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, unique=True, index=True, nullable=False)
    sku_id = sa.Column(sa.String(155), sa.ForeignKey('staging_local.general_skus.sku_id', ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=True)
    note = sa.Column(sa.String(55), nullable=True)