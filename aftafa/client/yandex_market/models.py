import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.dialects.postgresql import UUID as pg_UUID
from sqlalchemy.orm import Session, declarative_base

from aftafa.common.dal import postgres_url as db_url
from aftafa.client.yandex_market.enums import (
    OrderEntryItemPriceTypeEnum,
    WarehouseStockTypeEnum
)


Base = declarative_base()
engine = sa.create_engine(db_url)
session = Session(engine)


class Supplier(Base):
    """Represents supplier a.k.a legal entity for a given account"""

    __tablename__ = "supplier"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False)
    sale_schema = sa.Column(sa.String(10), nullable=False)


class Business(Base):
    """Represents business linked to a Yandex account. One account could have multiple businesses
    e.g. """
    __tablename__ = "business"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String(55), nullable=False)
    slug = sa.Column(sa.String(55), nullable=False)


class Campaign(Base):
    """Represents method of interacting with Yandex Market (e.g. FBY, FBS, DBS etc.)"""
    __tablename__ = "campaign"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    business_id = sa.Column(sa.Integer, sa.ForeignKey(Business.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = sa.Column(sa.String(55), nullable=False)
    slug = sa.Column(sa.String(55), nullable=False)


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=False)
    name = sa.Column(sa.String(100), nullable=False)


class ShopSku(Base):
    __tablename__ = "shop_sku"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    category_id = sa.Column(sa.Integer, sa.ForeignKey(Category.id, ondelete='CASCADE'), nullable=False)

    shop_sku = sa.Column(sa.String(80), index=True, nullable=False)
    market_sku = sa.Column(sa.String(120), nullable=True)
    name = sa.Column(sa.String(255), nullable=False)
    # category = sa.Column(sa.String(100), nullable=False)
    length = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    width = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    height = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    weight = sa.Column(sa.DECIMAL(12, 3), nullable=False, default=0)
    price = sa.Column(sa.DECIMAL(12, 2), nullable=True)


class Offer(Base):
    """
    Represents offer (part of offer mapping) from Yandex Market
    """

    __tablename__ = "offer"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    
    name = sa.Column(sa.String(255), nullable=False)
    shop_sku = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)
    category = sa.Column(sa.String(55), nullable=False)
    vendor = sa.Column(sa.String(55), nullable=False)
    vendor_code = sa.Column(sa.String(55), nullable=True)
    primary_image = sa.Column(sa.String(55), nullable=True)
    manufacturer = sa.Column(sa.String(155), nullable=True)
    manufacturer_country = sa.Column(sa.String(55), nullable=True)
    processing_state_status = sa.Column(sa.String(55), nullable=False)
    availability = sa.Column(sa.String(55), nullable=False)


class OfferBarcode(Base):
    """
    Represents offer barcodes (part of offer mapping) from Yandex Market
    """

    __tablename__ = "offer_barcode"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    offer_id = sa.Column(sa.Integer, sa.ForeignKey(Offer.id, ondelete='CASCADE'), nullable=False)

    barcode = sa.Column(sa.String(25), nullable=False)


class OfferPrice(Base):
    """
    
    """
    __tablename__ = "offer_price"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)
    
    shop_sku = sa.Column(sa.String(80), nullable=False)
    value = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    discount_base = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    currency_id = sa.Column(sa.String(25), nullable=True)
    vat = sa.Column(sa.Integer, nullable=True)

    updated_at = sa.Column(sa.DateTime, nullable=True)
    fetched_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class ShopSkuTariff(Base):
    __tablename__ = "shop_sku_tariff"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)

    tariff_type = sa.Column(sa.String(50), index=True, nullable=False)
    percent = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    amount = sa.Column(sa.DECIMAL(12, 2), nullable=True)


class Warehouse(Base):
    __tablename__ = "warehouse"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=False)
    name = sa.Column(sa.String(100), nullable=False)


class ShopSkuStocks(Base):
    __tablename__ = "shop_sku_stocks"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouse.id, ondelete='CASCADE'), nullable=False)

    stock_type = sa.Column(sa.String(50), nullable=False)
    stock_count = sa.Column(sa.Integer, nullable=False, default=0)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class Region(Base):
    __tablename__ = "region"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    name = sa.Column(sa.String(255), nullable=False)


class Order(Base):
    __tablename__ = "order"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True, nullable=False)
    order_id = sa.Column(sa.BIGINT, index=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)

    partner_order_id = sa.Column(sa.String(100), nullable=True)                                                     # Идентификатор заказа в информационной системе магазина.
    creation_date = sa.Column(sa.Date, nullable=False)
    status = sa.Column(sa.String(155), nullable=False)
    status_update_date = sa.Column(sa.DateTime, nullable=False)
    payment_type = sa.Column(sa.String(55), nullable=False)
    fake = sa.Column(sa.Boolean, nullable=True)
    delivery_region_id = sa.Column(sa.Integer, sa.ForeignKey(Region.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class OrderCommissions(Base):
    __tablename__ = "order_commissions"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    order_id = sa.Column(sa.BIGINT, sa.ForeignKey(Order.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    type = sa.Column(sa.String(55), nullable=False)
    actual = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    predicted = sa.Column(sa.DECIMAL(12, 2), nullable=True)


class OrderPayments(Base):
    __tablename__ = "order_payments"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    payment_id = sa.Column(sa.String(55), index=True, nullable=False)
    order_id = sa.Column(sa.BIGINT, sa.ForeignKey(Order.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    date = sa.Column(sa.Date, nullable=True)
    type = sa.Column(sa.String(55), nullable=False)
    source = sa.Column(sa.String(55), nullable=True)
    total = sa.Column(sa.DECIMAL(12, 2), nullable=False)


class OrderItem(Base):
    __tablename__ = "order_item"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    order_id = sa.Column(sa.BIGINT, sa.ForeignKey(Order.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouse.id, ondelete='CASCADE'), nullable=True)
    offer_name = sa.Column(sa.String(255), nullable=False)
    market_sku = sa.Column(sa.String(120), nullable=False)
    count = sa.Column(sa.Integer, nullable=False, default=0)
    initial_count = sa.Column(sa.Integer, nullable=False, default=0)


class OrderItemPrice(Base):
    __tablename__ = "order_item_price"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    order_item_id = sa.Column(sa.BIGINT, sa.ForeignKey(OrderItem.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    price_type = sa.Column(sa.Enum(OrderEntryItemPriceTypeEnum), nullable=False)
    cost_per_item = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    total = sa.Column(sa.DECIMAL(12, 2), nullable=False)


class OrderItemDetails(Base):
    __tablename__ = "order_item_details"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    order_item_id = sa.Column(sa.BIGINT, sa.ForeignKey(OrderItem.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    item_status = sa.Column(sa.String(55), nullable=False)
    item_count = sa.Column(sa.Integer, nullable=False)
    stock_type = sa.Column(sa.Enum(WarehouseStockTypeEnum), nullable=True)
    update_date = sa.Column(sa.Date, nullable=True)


class OrderItemCisList(Base):
    __tablename__ = "order_item_cis_list"
    __table_args__ = {"schema": "yandex"}

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    order_item_id = sa.Column(sa.BIGINT, sa.ForeignKey(OrderItem.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    cis = sa.Column(sa.String(150), nullable=False)
    

class UtFbsStocks(Base):
    __tablename__ = "ut_fbs_stocks"
    __table_args__ = (
            sa.UniqueConstraint(
                'supplier_id',
                'shop_sku_id',
                'updated_at'
            ),
            {
            "schema": 'yandex',
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)

    market_sku = sa.Column(sa.String(120), nullable=False)
    available = sa.Column(sa.Integer, nullable=False)
    warehouse = sa.Column(sa.String(120), nullable=True)
    status = sa.Column(sa.String(155), nullable=True)

    updated_at = sa.Column(sa.Date, nullable=False)


class UtFbsStocksV2(Base):
    __tablename__ = "ut_fbs_stocks_v2"
    __table_args__ = (
            sa.UniqueConstraint(
                'supplier_id',
                'shop_sku_id',
                'updated_at'
            ),
            {
            "schema": 'yandex',
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE'), nullable=False)
    shop_sku_id = sa.Column(sa.Integer, sa.ForeignKey(ShopSku.id, ondelete='CASCADE'), nullable=False)

    shop_sku_name = sa.Column(sa.String(255), nullable=True)
    errors = sa.Column(sa.Text, nullable=True)
    warnings = sa.Column(sa.Text, nullable=True)

    available = sa.Column(sa.Integer, nullable=False)

    updated_at = sa.Column(sa.Date, nullable=False)


# class WebSeller(Base):
#     __tablename__ = 'web_seller'
#     __table_args__ = {'schema': 'yandex'}

#     id = sa.Column(sa.Integer, primary_key=True)
#     name = sa.Column(sa.String(125), nullable=False)
#     supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class WebCatalogProduct(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'web_catalog_product'
    __table_args__ = {'schema': 'yandex'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    meta_supplier = sa.Column(sa.String(255), nullable=False)
    meta_report_date = sa.Column(sa.String(100), nullable=False)

    web_catalog_product_id = sa.Column(sa.String(255), nullable=True)
    model_id = sa.Column(sa.String(255), nullable=True)
    sku_id = sa.Column(sa.String(255), nullable=True)
    offer_id = sa.Column(sa.String(255), nullable=True)
    market_sku_creator = sa.Column(sa.String(255), nullable=True)
    price = sa.Column(sa.String(255), nullable=True)
    old_price = sa.Column(sa.String(255), nullable=True)
    merch_price = sa.Column(sa.String(255), nullable=True)
    vendor_id = sa.Column(sa.String(255), nullable=True)
    hid = sa.Column(sa.String(255), nullable=True)
    nid = sa.Column(sa.String(255), nullable=True)
    is_digital = sa.Column(sa.Boolean, nullable=True)
    offer_color = sa.Column(sa.String(255), nullable=True)
    product_id = sa.Column(sa.String(255), nullable=True)
    ware_id = sa.Column(sa.String(255), nullable=True)
    feed_id = sa.Column(sa.String(255), nullable=True)
    available_count = sa.Column(sa.Integer, nullable=True)
    shop_id = sa.Column(sa.String(255), nullable=True)
    supplier_id = sa.Column(sa.String(255), nullable=True)
    cashback_value = sa.Column(sa.String(255), nullable=True)
    shop_sku = sa.Column(sa.String(255), nullable=True)
    is_eda = sa.Column(sa.Boolean, nullable=True)
    is_express = sa.Column(sa.Boolean, nullable=True)
    warehouse_id = sa.Column(sa.String(255), nullable=True)
    is_any_express = sa.Column(sa.Boolean, nullable=True)
    is_bnpl = sa.Column(sa.Boolean, nullable=True)
    is_installments = sa.Column(sa.Boolean, nullable=True)
    business_id = sa.Column(sa.String(255), nullable=True)
    is_foodtech = sa.Column(sa.String(255), nullable=True)
    is_on_demand = sa.Column(sa.Boolean, nullable=True)
    ya_bank_price = sa.Column(sa.String(255), nullable=True)
    is_DSBS = sa.Column(sa.Boolean, nullable=True)
    has_resale_goods = sa.Column(sa.Boolean, nullable=True)
    pos = sa.Column(sa.String(255), nullable=True)
    req_id = sa.Column(sa.String(255), nullable=True)
    variant = sa.Column(sa.String(255), nullable=True)
    brand_name = sa.Column(sa.String(255), nullable=True)
    has_address = sa.Column(sa.String(255), nullable=True)
    has_badge_new = sa.Column(sa.Boolean, nullable=True)
    has_badge_exclusive = sa.Column(sa.Boolean, nullable=True)
    has_badge_rare = sa.Column(sa.Boolean, nullable=True)
    viewtype = sa.Column(sa.String(255), nullable=True)
    offers_count = sa.Column(sa.String(255), nullable=True)
    min_price = sa.Column(sa.String(255), nullable=True)
    is_connected_retail = sa.Column(sa.Boolean, nullable=True)
    web_catalog_product_type = sa.Column(sa.String(255), nullable=True)
    show_uid = sa.Column(sa.String(255), nullable=True)
    vat = sa.Column(sa.String(255), nullable=True)
    market_sku = sa.Column(sa.String(255), nullable=True)
    snippet_type = sa.Column(sa.String(255), nullable=True)
    
    extracted_at = sa.Column(sa.DateTime, nullable=False)
    

# class WebCatalogProductColor(Base):
#     """
#     Default mapping for local base SKUs' mapping from different schemas.
#     """
#     __tablename__ = 'web_catalog_product_color'
#     __table_args__ = {'schema': 'yandex'}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     web_catalog_product_id = sa.Column(sa.Integer, sa.ForeignKey(WebCatalogProduct.id), index=True, nullable=False)

#     color_id = sa.Column(sa.Integer)
#     color_name = sa.Column(sa.String(100))
    

# class WebCatalogProductSize(Base):
#     """
#     Default mapping for local base SKUs' mapping from different schemas.
#     """
#     __tablename__ = 'web_catalog_product_size'
#     __table_args__ = {'schema': 'yandex'}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     web_catalog_product_id = sa.Column(sa.Integer, sa.ForeignKey(WebCatalogProduct.id), index=True, nullable=False)

#     name = sa.Column(sa.String(255), nullable=True)
#     orig_name = sa.Column(sa.String(255), nullable=True)
#     rank = sa.Column(sa.String(255), nullable=True)
#     option_id = sa.Column(sa.String(255), nullable=True)
#     wh = sa.Column(sa.String(255), nullable=True)
#     dtype = sa.Column(sa.String(255), nullable=True)
#     sale_conditions = sa.Column(sa.String(255), nullable=True)
#     payload = sa.Column(sa.String(255), nullable=True)

#     price_basic = sa.Column(sa.String(255), nullable=True)
#     price_product = sa.Column(sa.String(255), nullable=True)
#     price_total = sa.Column(sa.String(255), nullable=True)
#     price_logistics = sa.Column(sa.String(255), nullable=True)
#     price_return_ =sa.Column(sa.String(255), nullable=True)
    
#     extracted_at = sa.Column(sa.DateTime, nullable=False)
