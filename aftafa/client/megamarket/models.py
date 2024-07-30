import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy.sql import func

from aftafa.common.dal import postgres_url as db_url


DEFAULT_SCHEMA: str = 'sbermm'

Base = declarative_base()
engine = sa.create_engine(db_url)
session = Session(engine)


class Account(Base):
    """Represents supplier a.k.a legal entity for a given account"""
    __tablename__ = 'account'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False)
    slug = sa.Column(sa.String(55), nullable=False)


class Merchant(Base):
    """
    """
    __tablename__ = 'merchant'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, unique=True, primary_key=True, nullable=False)
    account_id = sa.Column(sa.Integer, sa.ForeignKey(Account.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)

    name = sa.Column(sa.String(100), nullable=False)
    slug = sa.Column(sa.String(100), nullable=True)
    private = sa.Column(sa.Boolean, nullable=False, default=False)


class MerchantInfo(Base):
    """
    """
    __tablename__ = 'merchant_info'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    merchant_id = sa.Column(sa.Integer, unique=True, primary_key=True, nullable=False)
    account_id = sa.Column(sa.Integer, sa.ForeignKey(Account.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    slug = sa.Column(sa.String(100), nullable=True)

    merchant_name = sa.Column(sa.String(255), nullable=True)
    full_name = sa.Column(sa.String(255), nullable=True)
    partner_id = sa.Column(sa.String(255), nullable=False)
    phone = sa.Column(sa.String(100), nullable=True)
    email = sa.Column(sa.String(100), nullable=True)
    contract_id = sa.Column(sa.String(100), nullable=True)
    
    stock_source = sa.Column(sa.String(100), nullable=True)
    stock_url = sa.Column(sa.String(255), nullable=True)
    time_zone = sa.Column(sa.String(100), nullable=True)
    token = sa.Column(sa.String(255), nullable=True)
    web_site_url = sa.Column(sa.String(255), nullable=True)
    feed_load_rate = sa.Column(sa.Integer, nullable=True)
    feed_url = sa.Column(sa.String(255), nullable=True)
    auto_rating = sa.Column(sa.Integer, nullable=True)
    static_rating = sa.Column(sa.Integer, nullable=True)
    date_create = sa.Column(sa.String(100), nullable=True)
    date_update = sa.Column(sa.String(100), nullable=True)

    auto_cancel_orders = sa.Column(sa.Boolean)
    auto_confirm_orders = sa.Column(sa.Boolean)
    auto_confirmation_by_EAN = sa.Column(sa.Boolean)
    auto_confirmation_by_EAN_user_id = sa.Column(sa.Integer, nullable=True)
    automatic_stock_size = sa.Column(sa.Integer, nullable=True)
    confirmation_duration = sa.Column(sa.Integer, nullable=True)
    confirmation_schedule_id = sa.Column(sa.String(100), nullable=True)
    hide_offers_order_daily_limit = sa.Column(sa.Integer, nullable=True)
    integration_is_active = sa.Column(sa.Boolean)
    integration_order_cancel_url = sa.Column(sa.String(100), nullable=True)
    integration_order_lable_update_url = sa.Column(sa.String(100), nullable=True)
    integration_order_new_url = sa.Column(sa.String(100), nullable=True)
    is_active = sa.Column(sa.Boolean)
    is_agreeing_to_the_terms_of_the_SBPG = sa.Column(sa.Boolean)
    is_blocked_by_merchant_cc = sa.Column(sa.Boolean)
    is_blocked_by_merchant_delivery = sa.Column(sa.Boolean)
    is_CC_order_section_enabled = sa.Column(sa.Boolean)
    is_change_date_of_shipment = sa.Column(sa.Boolean)
    is_DSM_order_section_enabled = sa.Column(sa.Boolean)
    is_delivery_order_section_enabled = sa.Column(sa.Boolean)
    is_feed_monitoring = sa.Column(sa.Boolean)
    is_mcs_section_enabled = sa.Column(sa.Boolean)
    is_notify_order_email = sa.Column(sa.Boolean)
    is_notify_order_SMS = sa.Column(sa.Boolean)
    is_personal_data_sending_available = sa.Column(sa.Boolean)
    is_print_name_on_marking_sheet = sa.Column(sa.Boolean)
    is_SBPG_lock = sa.Column(sa.Boolean)
    is_self_registration = sa.Column(sa.Boolean)
    is_services_section_available = sa.Column(sa.Boolean)
    is_shipment_part = sa.Column(sa.Boolean)
    is_sticker_tuning_enabled = sa.Column(sa.Boolean)
    is_unboxed_return = sa.Column(sa.Boolean)
    is_use_shipment_days_long = sa.Column(sa.Boolean)
    last_feed_date = sa.Column(sa.String(100), nullable=True)
    max_shipment_days = sa.Column(sa.Integer, nullable=True)
    orders_daily_limit = sa.Column(sa.Integer, nullable=True)
    test_period_end_date = sa.Column(sa.String(100), nullable=True)
    test_period_end_date_CC = sa.Column(sa.String(100), nullable=True)
    test_period_end_date_DBM = sa.Column(sa.String(100), nullable=True)
    use_auto_rating = sa.Column(sa.Boolean)
    CC_stock_feed_host = sa.Column(sa.String(100), nullable=True)
    CC_stock_feed_login = sa.Column(sa.String(100), nullable=True)
    CC_stock_feed_pass = sa.Column(sa.String(100), nullable=True)
    CC_stock_feed_path = sa.Column(sa.String(100), nullable=True)
    CC_stock_feed_port = sa.Column(sa.String(100), nullable=True)


class CatalogItem(Base):
    """
    """
    __tablename__ = 'catalog_item'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    catalog_item_id = sa.Column(sa.String(150), nullable=False, unique=True)                                                         # it's like id for a catalog item entry
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    date_confirmation = sa.Column(sa.DateTime, nullable=True)
    publication_status = sa.Column(sa.String(150), nullable=False)
    publication_status_humanized = sa.Column(sa.String(150), nullable=False)
    can_unlock = sa.Column(sa.Boolean, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    

class MerchantGoods(Base):
    """
    """
    __tablename__ = 'merchant_goods'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    merchant_goods_id = sa.Column(sa.String(150), primary_key=True, nullable=False)
    merchant_offer_id = sa.Column(sa.String(50), nullable=False)
    catalog_item_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(CatalogItem.id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )

    delivery = sa.Column(sa.Boolean, nullable=True)
    pickup = sa.Column(sa.Boolean, nullable=True)
    store = sa.Column(sa.Boolean, nullable=True)
    url = sa.Column(sa.String(255), nullable=True)
    picture = sa.Column(sa.String(255), nullable=True)
    name = sa.Column(sa.String(255), nullable=True)
    merchant_offer_name = sa.Column(sa.String(255), nullable=True)
    barcode = sa.Column(sa.String(55), nullable=True)
    vendor = sa.Column(sa.String(55), nullable=True)
    vendor_code = sa.Column(sa.String(55), nullable=True)
    category_id = sa.Column(sa.Integer, nullable=False)
    category_path = sa.Column(sa.String(255), nullable=True)
    currency_id = sa.Column(sa.String(25), nullable=False, default='RUR')
    
    price = sa.Column(sa.Integer, nullable=True)


class MerchantGoodsOutlets(Base):
    """
    """
    __tablename__ = 'merchant_goods_outlets'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    outlet_id = sa.Column(sa.Integer, nullable=False)
    merchant_goods_id = sa.Column(sa.String(150), sa.ForeignKey(MerchantGoods.merchant_goods_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    instock = sa.Column(sa.Integer, nullable=False)


class SuggestedGoods(Base):
    """
    """
    __tablename__ = 'suggested_goods'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    suggested_goods_id = sa.Column(sa.String(150), primary_key=True, nullable=False)
    goods_id = sa.Column(sa.String(100), index=True, nullable=False)
    catalog_item_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(CatalogItem.id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    item_id = sa.Column(sa.String(100), nullable=False)

    rate = sa.Column(sa.Integer, nullable=True)
    date_activate = sa.Column(sa.Date, nullable=True)
    single_offer_card = sa.Column(sa.Boolean, nullable=True)
    short_web_name = sa.Column(sa.String(255), nullable=True)
    brand = sa.Column(sa.String(100), nullable=True)
    brand_slug = sa.Column(sa.String(100), nullable=True)
    gtin = sa.Column(sa.String(100), nullable=True)
    logistic_class = sa.Column(sa.String(155), nullable=True)
    logistic_class_code = sa.Column(sa.Integer, nullable=True)
    logistic_class_type = sa.Column(sa.Integer, nullable=True)
    manufacturer_part_no = sa.Column(sa.String(100), nullable=True)
    model = sa.Column(sa.String(100), nullable=True)
    multiboxes_possible = sa.Column(sa.String(100), nullable=True)
    nds = sa.Column(sa.String(55), nullable=True)
    flags = sa.Column(sa.String(255), nullable=True)
    update_at = sa.Column(sa.Date, nullable=True)
    publication_date = sa.Column(sa.DateTime, nullable=True)
    url = sa.Column(sa.String(155), nullable=True)
    reviews_count = sa.Column(sa.Integer, nullable=True)
    reviews_rating = sa.Column(sa.Integer, nullable=True)
    reviews_show = sa.Column(sa.Integer, nullable=True)
    quality = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    category_master = sa.Column(sa.String(155), nullable=True)
    

class SuggestedGoodsMerchantRates(Base):
    """
    """
    __tablename__ = 'suggested_goods_merchant_rates'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    suggested_goods_id = sa.Column(sa.String(150), sa.ForeignKey(SuggestedGoods.suggested_goods_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    service_scheme = sa.Column(sa.String(55), nullable=False)
    rate = sa.Column(sa.Integer, nullable=True)
    min_fee = sa.Column(sa.Integer, nullable=True)


class SuggestedGoodsPrices(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    suggested_goods_id = sa.Column(sa.String(150), sa.ForeignKey(SuggestedGoods.suggested_goods_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    is_available = sa.Column(sa.Boolean, nullable=False)
    price_date = sa.Column(sa.DateTime, nullable=True)
    last_price = sa.Column(sa.Integer, nullable=True)
    final_price = sa.Column(sa.Integer, nullable=True)
    crossed_price = sa.Column(sa.Integer, nullable=True)
    crossed_price_term = sa.Column(sa.String(100), nullable=True)
    min_price = sa.Column(sa.Integer, nullable=True)
    max_price = sa.Column(sa.Integer, nullable=True)
    total_offers = sa.Column(sa.Integer, nullable=True)
    delivery_date = sa.Column(sa.Date, nullable=True)
    price_change_percentage = sa.Column(sa.DECIMAL(12, 2), nullable=True)


class SuggestedGoodsPricesFavoriteOffer(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices_favorite_offer'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    offer_id = sa.Column(sa.String(155), index=True, nullable=False)
    goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    price = sa.Column(sa.Integer, nullable=False)
    partner_id = sa.Column(sa.String(100), nullable=True)
    contract_id = sa.Column(sa.String(100), nullable=True)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    merchant_name = sa.Column(sa.String(100), nullable=True)
    old_price = sa.Column(sa.Integer, nullable=True)


class SuggestedGoodsPricesOffers(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices_offers'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    price = sa.Column(sa.Integer, nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    merchant_name = sa.Column(sa.String(100), nullable=False)
    type = sa.Column(sa.String(100), nullable=True)


# class SuggestedGoodsPricesBonus(Base):
#     """
#     """
#     __tablename__ = 'suggested_goods_prices_bonus'
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
#     goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

#     k = sa.Column(sa.Integer, nullable=False)
#     bonus_date = sa.Column(sa.DateTime, nullable=True)


class SuggestedGoodsPricesBonusMerchantBonus(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices_bonus_merchant_bonus'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    merchant_name = sa.Column(sa.String(100), nullable=False)
    k = sa.Column(sa.Integer, nullable=False)
    bonus_date = sa.Column(sa.DateTime, nullable=True)


class SuggestedGoodsPricesPriceHistory(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices_price_history'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    point_id = sa.Column(sa.Integer, nullable=False)
    point_value = sa.Column(sa.Integer, nullable=False)
    point_name = sa.Column(sa.String(100), nullable=False)


class SuggestedGoodsPricesPriceAdjustments(Base):
    """
    """
    __tablename__ = 'suggested_goods_prices_price_adjustments'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    goods_prices_id = sa.Column(sa.Integer, sa.ForeignKey(SuggestedGoodsPrices.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    amount = sa.Column(sa.Integer, nullable=False) 
    type = sa.Column(sa.String(100), nullable=False)


class SuggestedGoodsOffersV2(Base):
    """
    """
    __tablename__ = 'suggested_goods_offers_v2'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    suggested_goods_id = sa.Column(sa.String(150), sa.ForeignKey(SuggestedGoods.suggested_goods_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    price = sa.Column(sa.Integer, nullable=False)
    old_price = sa.Column(sa.Integer, nullable=True)    
    service_scheme = sa.Column(sa.String(100), nullable=True)
    type = sa.Column(sa.String(100), nullable=True)
    favorite = sa.Column(sa.Boolean, nullable=False)
    group = sa.Column(sa.Integer, nullable=True)


class SuggestedGoodsBox(Base):
    """
    """
    __tablename__ = 'suggested_goods_box'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    suggested_goods_id = sa.Column(sa.String(150), sa.ForeignKey(SuggestedGoods.suggested_goods_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    box_id = sa.Column(sa.Integer, nullable=False)

    packaging_unit = sa.Column(sa.String(25), nullable=False)
    weight_unit = sa.Column(sa.String(25), nullable=False)
    width = sa.Column(sa.Integer, nullable=False)
    height = sa.Column(sa.Integer, nullable=False)
    length = sa.Column(sa.Integer, nullable=False)
    weight = sa.Column(sa.Integer, nullable=False)


class Category(Base):
    """
    """
    __tablename__ = 'category'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    category_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    structure_id = sa.Column(sa.Integer, nullable=True)
    name = sa.Column(sa.String(255), nullable=False)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('sbermm.category.category_id'), nullable=True)


class LocalMapping(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'local_mapping'
    __table_args__ = {'schema': DEFAULT_SCHEMA}

    catalog_item_id = sa.Column(
        sa.String(150),
        sa.ForeignKey(CatalogItem.catalog_item_id, ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )
    sku_id = sa.Column(
        sa.String(155),
        sa.ForeignKey('staging_local.general_skus.sku_id', ondelete='CASCADE', onupdate='CASCADE'),
        index=True,
        nullable=True
    )
    note = sa.Column(sa.String(55), nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())


class Order(Base):
    """
    """
    __tablename__ = 'order'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    uid = sa.Column(sa.String(25), unique=True, nullable=False)
    shipment_id = sa.Column(sa.String(13), nullable=False)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    delivery_id = sa.Column(sa.String(13), nullable=False)
    order_code = sa.Column(sa.String(15), nullable=True)
    shipment_is_changeable = sa.Column(sa.Boolean, nullable=False)
    
    confirmed_time_limit = sa.Column(sa.DateTime, nullable=True)
    packing_time_limit = sa.Column(sa.DateTime, nullable=True)
    shipping_time_limit = sa.Column(sa.DateTime, nullable=True)
    shipment_date_from = sa.Column(sa.DateTime, nullable=True)
    shipment_date_to = sa.Column(sa.DateTime, nullable=True)
    creation_date = sa.Column(sa.DateTime, nullable=False)
    delivery_date = sa.Column(sa.DateTime, nullable=False)
    delivery_date_from = sa.Column(sa.DateTime, nullable=False)
    delivery_date_to = sa.Column(sa.DateTime, nullable=False)
    reserve_expiration_date = sa.Column(sa.DateTime, nullable=True)
    
    customer_full_name = sa.Column(sa.String(55), nullable=True)
    customer_address = sa.Column(sa.String(255), nullable=True)
    shipping_point = sa.Column(sa.String(55), nullable=False)
    shipment_date_shift = sa.Column(sa.Boolean, nullable=False)
    
    delivery_method_id = sa.Column(sa.String(25), nullable=False)
    service_scheme = sa.Column(sa.String(25), nullable=False)
    deposited_amount = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    
    meta_created_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())
    
    
class OrderCustomer(Base):
    """
    """
    __tablename__ = 'order_customer'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    order_uid = sa.Column(sa.String(25), sa.ForeignKey(Order.uid, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    first_name = sa.Column(sa.String(55), nullable=True)
    last_name = sa.Column(sa.String(55), nullable=True)
    middle_name = sa.Column(sa.String(55), nullable=True)
    email = sa.Column(sa.String(55), nullable=True)
    phone = sa.Column(sa.String(55), nullable=True)
    
    meta_created_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())
    
    
class OrderItem(Base):
    """
    """
    __tablename__ = 'order_item'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    order_uid = sa.Column(sa.String(25), sa.ForeignKey(Order.uid, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    catalog_item_id = sa.Column(sa.String(150), sa.ForeignKey(CatalogItem.catalog_item_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    order_position_id = sa.Column(sa.String(55), unique=True, nullable=False)

    is_cancelation_pending = sa.Column(sa.Boolean, nullable=False)
    item_index = sa.Column(sa.String(25), nullable=False)
    status = sa.Column(sa.String(55), nullable=False)
    sub_status = sa.Column(sa.String(55), nullable=True)
    price = sa.Column(sa.Integer, nullable=False)
    final_price = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    offer_id = sa.Column(sa.String(55), nullable=False)
    goods_id = sa.Column(sa.String(55), nullable=False)
    digital_mark = sa.Column(sa.String(155), nullable=True)
    
    meta_created_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())
    
    
class OrderItemDiscount(Base):
    """
    """
    __tablename__ = 'order_item_discount'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    order_position_id = sa.Column(
        sa.String(55),
        sa.ForeignKey(OrderItem.order_position_id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    # order_item_id = sa.Column(sa.BigInteger, sa.ForeignKey(OrderItem.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    discount_type = sa.Column(sa.String(55), nullable=False)
    discount_description = sa.Column(sa.String(155), nullable=False)
    discount_amount = sa.Column(sa.Integer, nullable=False)
        
    meta_created_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())
    
    
class OrderItemGoodsData(Base):
    """
    """
    __tablename__ = 'order_item_goods_data'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    order_position_id = sa.Column(
        sa.String(55),
        sa.ForeignKey(OrderItem.order_position_id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )
    # order_item_id = sa.Column(sa.BigInteger, sa.ForeignKey(OrderItem.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    is_digital_mark_required = sa.Column(sa.Boolean, nullable=False)
        
    meta_created_at = sa.Column(sa.TIMESTAMP, nullable=False, default=func.now())


    

class Stock(Base):
    """
    """
    __tablename__ = 'stock'
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    merchant_id = sa.Column(sa.Integer, sa.ForeignKey(Merchant.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    catalog_item_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(CatalogItem.id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False
    )


    facility_id = sa.Column(sa.String(255), nullable=False)
    item_id = sa.Column(sa.String(55), nullable=False)
    item_name = sa.Column(sa.String(255), nullable=True)

    fact_quality = sa.Column(sa.String(55), nullable=False)
    fact_quantity = sa.Column(sa.Integer, nullable=False)
    value = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    volume_weight = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    is_digital_mark_required = sa.Column(sa.Boolean, nullable=True)
    
    extracted_at = sa.Column(sa.DateTime, nullable=True)
    updated_at = sa.Column(sa.DateTime, nullable=True)
