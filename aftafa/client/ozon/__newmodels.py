import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql import func

from aftafa.common.dal import (
    postgres_url as db_url,
    engine as db_engine,
    session as db_session
)
from aftafa.client.ozon.schemas import (
    AdvObjectTypeEnum,
    CampaignStateEnum,
    PerfSearchBidRelevanceEnum,
    ProductCampaignPlacementEnum,
    TplIntegrationEnum, 
    FbsReturnStatusEnum, 
    FinancialTransactionTypeEnum, 
    FinancialDeliverySchemaEnum, 
    WarehouseFirstMileTypeEnum
)
from aftafa.client.ozon.db import Base


class Category(Base):
    __tablename__ = 'categories'

    category_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(100), nullable=False)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('categories.category_id'))


class CategoryTreeItem(Base):
    __tablename__ = 'category_tree_item'

    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    _parent_id = sa.Column(sa.Integer, nullable=True)
    description_category_id = sa.Column(sa.Integer, nullable=True)
    category_name = sa.Column(sa.String(100), nullable=True)
    disabled = sa.Column(sa.Boolean, nullable=False)
    type_id = sa.Column(sa.Integer, nullable=True)
    type_name = sa.Column(sa.String(100), nullable=True)


class TestCategoryTreeItem(Base):
    __tablename__ = 'test_category_tree_item'

    _id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    _parent_id = sa.Column(sa.Integer, nullable=True)
    description_category_id = sa.Column(sa.Integer, nullable=True)
    category_name = sa.Column(sa.String(100), nullable=True)
    disabled = sa.Column(sa.Boolean, nullable=False)
    type_id = sa.Column(sa.Integer, nullable=True)
    type_name = sa.Column(sa.String(100), nullable=True)


class Supplier(Base):
    __tablename__ = 'suppliers'

    supplier_id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name = sa.Column(sa.String(100), nullable=False)


class Product(Base):
    __tablename__ = "products"

    product_id = sa.Column(sa.Integer, primary_key=True, nullable=False, unique=True)
    offer_id = sa.Column(sa.Integer, nullable=False, unique=True)
    supplier_id = sa.Column(sa.Integer, nullable=False, unique=False)
    barcode = sa.Column(sa.String(100))
    category_id = sa.Column(sa.Integer, sa.ForeignKey(Category.category_id), nullable=True)
    category_tree_item_id = sa.Column(sa.Integer, sa.ForeignKey(CategoryTreeItem._id), nullable=True)
    description_category_id = sa.Column(sa.Integer, nullable=True)
    type_id = sa.Column(sa.Integer, nullable=True)
    color_image = sa.Column(sa.String(100))
    created_at = sa.Column(sa.DateTime, default=func.now())
    primary_image = sa.Column(sa.String(100))
    name = sa.Column(sa.String(500), nullable=False, default='no_name_yet')
    is_kgt = sa.Column(sa.Boolean, nullable=False, default=False)
    visible = sa.Column(sa.Boolean)
    sku = sa.Column(sa.BIGINT, nullable=True)
     

class ProductSource(Base):
    __tablename__ = "product_sources"

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False, unique=True)
    is_enabled = sa.Column(sa.Boolean)
    sku = sa.Column(sa.Integer, primary_key=True, nullable=False, unique=True)
    source = sa.Column(sa.String(25), nullable=False)


class ProductAttributes(Base):
    __tablename__ = "product_attributes"

    # id = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), primary_key=True, nullable=False, unique=True)
    height = sa.Column(sa.Integer)
    depth = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    weight = sa.Column(sa.Integer)
    weight_unit = sa.Column(sa.String(55))
    dimension_unit = sa.Column(sa.String(55))
    brand = sa.Column(sa.String(255))
    model = sa.Column(sa.String(255))
    commercial_type = sa.Column(sa.String(255))
    volume_weight = sa.Column(sa.Float)


class ProductRatings(Base):
    __tablename__ = "product_ratings"

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), primary_key=True, nullable=False, unique=True)
    rating = sa.Column(sa.DECIMAL(12, 2), nullable=False)


class ProductBarcodes(Base):
    __tablename__ = "product_barcodes"

    id = sa.Column(sa.String(125), primary_key=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    barcode = sa.Column(sa.String(100), nullable=False)


class ProductStocks(Base):
    __tablename__ = "product_stocks"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False, unique=True)
    type = sa.Column(sa.String(55))
    present = sa.Column(sa.Integer, default=0)
    reserved = sa.Column(sa.Integer, default=0)


class TSProductStocks(Base):
    __tablename__ = "ts_product_stocks"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False, unique=True)
    present = sa.Column(sa.Integer, default=0)
    reserved = sa.Column(sa.Integer, default=0)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class ProductPrices(Base):
    __tablename__ = "product_prices"

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), primary_key=True, nullable=False)
    buybox_price = sa.Column(sa.Integer)
    marketing_price = sa.Column(sa.Integer)
    marketing_seller_price = sa.Column(sa.Integer)
    min_price = sa.Column(sa.Integer)
    min_ozon_price = sa.Column(sa.Integer)
    old_price = sa.Column(sa.Integer)
    premium_price = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
    price_index = sa.Column(sa.Float)
    recommended_price = sa.Column(sa.Integer)
    vat = sa.Column(sa.Float)


class TSProductPrices(Base):
    __tablename__ = "ts_product_prices"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False, unique=True)
    marketing_price = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
    old_price = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class ProductCommissions(Base):
    __tablename__ = "product_commissions"

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), primary_key=True, nullable=False)
    fbo_deliv_to_customer_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_direct_flow_trans_max_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_direct_flow_trans_min_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_fulfillment_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_return_flow_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_return_flow_trans_min_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbo_return_flow_trans_max_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)

    fbs_deliv_to_customer_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_direct_flow_trans_max_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_direct_flow_trans_min_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_first_mile_min_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_first_mile_max_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_return_flow_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_return_flow_trans_max_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    fbs_return_flow_trans_min_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    sales_percent = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)


class Actions(Base):
    __tablename__ = "actions"

    action_id = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False)
    action_type = sa.Column(sa.String(155), nullable=False)
    title = sa.Column(sa.String(255))
    description = sa.Column(sa.Text())
    date_start = sa.Column(sa.DateTime)
    date_end = sa.Column(sa.DateTime)
    with_targeting = sa.Column(sa.Boolean)
    discount_type = sa.Column(sa.String(100))
    discount_value = sa.Column(sa.Float)
    order_amount = sa.Column(sa.Integer)
    is_voucher_action = sa.Column(sa.Boolean)


class SupplierActions(Base):
    __tablename__ = "supplier_actions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    action_id = sa.Column(sa.Integer, sa.ForeignKey(Actions.action_id), nullable=False)
    potential_products_count = sa.Column(sa.Integer)
    participating_products_count = sa.Column(sa.Integer)
    is_participating = sa.Column(sa.Boolean)
    banned_products_count = sa.Column(sa.Integer)
    freeze_date = sa.Column(sa.DateTime)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)


class ActionCandidates(Base):
    __tablename__ = "action_candidates"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    action_id = sa.Column(sa.Integer, sa.ForeignKey(Actions.action_id), nullable=False)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False)
    price = sa.Column(sa.Integer)
    action_price = sa.Column(sa.Integer)
    max_action_price = sa.Column(sa.Float)
    add_mode = sa.Column(sa.String(100))
    min_stock = sa.Column(sa.Integer)
    stock = sa.Column(sa.Integer)


class ActionProducts(Base):
    __tablename__ = "action_products"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    action_id = sa.Column(sa.Integer, sa.ForeignKey(Actions.action_id), nullable=False)
    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id), nullable=False)
    price = sa.Column(sa.Integer)
    action_price = sa.Column(sa.Integer)
    max_action_price = sa.Column(sa.Float)
    add_mode = sa.Column(sa.String(100))
    min_stock = sa.Column(sa.Integer)
    stock = sa.Column(sa.Integer)


class Warehouses(Base):
    __tablename__ = "warehouses"

    warehouse_id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    name = sa.Column(sa.String(100), nullable=False)
    is_rfbs = sa.Column(sa.Boolean)
    is_able_to_set_price = sa.Column(sa.Boolean)
    has_entrusted_acceptance = sa.Column(sa.Boolean)
    can_print_act_in_advance = sa.Column(sa.Boolean, nullable=False, default=True)
    has_postings_limit = sa.Column(sa.Boolean, nullable=False, default=False)
    is_karantin = sa.Column(sa.Boolean, nullable=False, default=False)
    is_kgt = sa.Column(sa.Boolean, nullable=False, default=False)
    is_timetable_editable = sa.Column(sa.Boolean, nullable=False, default=False)
    min_postings_limit = sa.Column(sa.Integer, nullable=False, default=10)
    postings_limit = sa.Column(sa.Integer, nullable=False, default=-1)
    min_working_days = sa.Column(sa.Integer, nullable=False, default=5)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)


class WarehouseFirstMileTypes(Base):
    __tablename__ = "warehouse_first_mile_types"
    
    dropoff_point_id = sa.Column(sa.String(55), nullable=True)
    dropoff_timeslot_id = sa.Column(sa.Integer, nullable=False, default=0)
    first_mile_is_changing = sa.Column(sa.Boolean, nullable=False, default=False)
    first_mile_type = sa.Column(sa.Enum(WarehouseFirstMileTypeEnum), nullable=False)
    warehouse_id = sa.Column(sa.BIGINT, sa.ForeignKey(Warehouses.warehouse_id), primary_key=True, nullable=False)


class WarehouseDeliveryMethods(Base):
    __tablename__ = "warehouse_delivery_methods"

    delivery_method_id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    name = sa.Column(sa.String(150), nullable=False)
    created_at = sa.Column(sa.DateTime, default=func.now())
    cutoff = sa.Column(sa.String(50))
    status = sa.Column(sa.String(50))
    provider_id = sa.Column(sa.Integer, nullable=False)
    template_id = sa.Column(sa.Integer, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=func.now())
    warehouse_id = sa.Column(sa.BigInteger, sa.ForeignKey(Warehouses.warehouse_id), nullable=True)
    company_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)


class ProductStocksFBS(Base):
    __tablename__ = "product_stocks_fbs"

    id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, autoincrement=True)
    fbs_sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku, ondelete='CASCADE'), nullable=False)
    fbs_warehouse = sa.Column(sa.BigInteger, sa.ForeignKey(Warehouses.warehouse_id, ondelete='CASCADE'), nullable=False)

    present = sa.Column(sa.Integer, nullable=False, default=0)
    reserved = sa.Column(sa.Integer, nullable=False, default=0)


class SupplyOrders(Base):
    __tablename__ = "supply_orders"

    supply_order_id = sa.Column(sa.BigInteger, primary_key=True, nullable=False, unique=True)
    supply_order_number = sa.Column(sa.String(155), unique=True, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)
    
    state = sa.Column(sa.String(55), nullable=False)
    created_at = sa.Column(sa.Date, nullable=False)
    local_timeslot = sa.Column(sa.DateTime, nullable=True)
    supply_warehouse_id = sa.Column(sa.String(55), nullable=True)
    supply_warehouse_name = sa.Column(sa.String(155), nullable=True)
    

class SupplyOrderItems(Base):
    __tablename__ = "supply_order_items"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    supply_order_id = sa.Column(sa.BigInteger, sa.ForeignKey(SupplyOrders.supply_order_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    offer_id = sa.Column(sa.String(100), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    
    
class FBOPostings(Base):
    __tablename__ = "fbo_postings"

    posting_number = sa.Column(sa.String(50), primary_key=True, nullable=False, unique=True)
    order_id = sa.Column(sa.BigInteger, nullable=False)                                             # FIXME: changed to bigint lately
    order_number = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(25), nullable=False)
    cancel_reason_id = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False)
    in_process_at = sa.Column(sa.DateTime, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)

    def __repr__(self) -> str:
        return f"<FBO Posting {self.posting_number}"


class FBOPostingsAnalyticsData(Base):
    __tablename__ = "fbo_postings_analytics_data"

    order_number = sa.Column(sa.String(50), nullable=False)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), primary_key=True, nullable=False)
    region = sa.Column(sa.String(155), nullable=True)
    city = sa.Column(sa.String(55), nullable=True)
    delivery_type = sa.Column(sa.String(55), nullable=True)
    is_premium = sa.Column(sa.Boolean, nullable=False)
    payment_type_group_name = sa.Column(sa.String(55), nullable=False)
    warehouse_id = sa.Column(sa.BIGINT, nullable=False)
    warehouse_name = sa.Column(sa.String(55), nullable=False)
    is_legal = sa.Column(sa.Boolean, nullable=False)


class FBOPostingsProducts(Base):
    __tablename__ = "fbo_postings_products"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=False, primary_key=True)
    name = sa.Column(sa.String(500))
    quantity = sa.Column(sa.Integer, nullable=False)
    offer_id = sa.Column(sa.String(100))
    price = sa.Column(sa.Integer, nullable=False)


class FBOPostingsPostingServices(Base):
    __tablename__ = "fbo_postings_posting_services"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=False, primary_key=True)
    marketplace_service_item_fulfillment = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_pickup = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_pvz = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_sc = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_ff = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_direct_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_not_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_part_goods_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_after_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)


class FBOPostingsProductsFinData(Base):
    __tablename__ = "fbo_postings_products_findata"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=False, primary_key=True)
    commission_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    commission_percent = sa.Column(sa.Integer, nullable=False, default=0)
    payout = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    old_price = sa.Column(sa.Integer, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    total_discount_percent = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    total_discount_value = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    client_price = sa.Column(sa.Integer, nullable=True)
    
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbo_postings_products.posting_number', 'fbo_postings_products.sku']
        ),
    )


class FBOPostingsProductsFinDataActions(Base):
    __tablename__ = "fbo_postings_products_findata_actions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=False)
    sold_on_action = sa.Column(sa.String(255), nullable=False)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbo_postings_products_findata.posting_number', 'fbo_postings_products_findata.sku']
        ),
    )


class FBOPostingsProductsFinDataItemServices(Base):
    __tablename__ = "fbo_postings_products_findata_item_services"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=False, primary_key=True)
    marketplace_service_item_fulfillment = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_pickup = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_pvz = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_sc = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_ff = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_direct_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_not_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_part_goods_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_after_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbo_postings_products_findata.posting_number', 'fbo_postings_products_findata.sku']
        ),
    )


# --------------------------------------------------
class FBSPostings(Base):
    __tablename__ = "fbs_postings"

    posting_number = sa.Column(sa.String(50), primary_key=True, nullable=False, unique=True)
    order_id = sa.Column(sa.BigInteger, nullable=False)                                             # FIXME: changed to bigint lately
    order_number = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(25), nullable=False)
    tracking_number = sa.Column(sa.String(100), nullable=True)
    tpl_integration_type = sa.Column(sa.Enum(TplIntegrationEnum), nullable=False)
    in_process_at = sa.Column(sa.DateTime, nullable=False)
    shipment_date = sa.Column(sa.DateTime, nullable=True)
    delivering_date = sa.Column(sa.DateTime, nullable=True)
    barcodes = sa.Column(sa.Boolean)
    is_express = sa.Column(sa.Boolean, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)

class FBSPostingsDeliveryMethod(Base):
    __tablename__ = "fbs_postings_delivery_method"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), primary_key=True, nullable=False)
    delivery_method_id = sa.Column(sa.Integer, sa.ForeignKey(WarehouseDeliveryMethods.delivery_method_id), nullable=False)
    delivery_method_name = sa.Column(sa.String(155), nullable=False)
    warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouses.warehouse_id), nullable=False)
    warehouse_name = sa.Column(sa.String(155), nullable=False)
    tpl_provider_id = sa.Column(sa.Integer, nullable=False)
    tpl_provider = sa.Column(sa.String(155), nullable=False)


class FBSPostingsAnalyticsData(Base):
    __tablename__ = "fbs_postings_analytics_data"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), primary_key=True, nullable=False)
    region = sa.Column(sa.String(155), nullable=True)
    city = sa.Column(sa.String(55), nullable=True)
    delivery_type = sa.Column(sa.String(55), nullable=True)
    is_premium = sa.Column(sa.Boolean, nullable=False)
    payment_type_group_name = sa.Column(sa.String(55), nullable=False)
    delivery_date_begin = sa.Column(sa.DateTime, nullable=True)
    delivery_date_end = sa.Column(sa.DateTime, nullable=True)
    is_legal = sa.Column(sa.Boolean, nullable=False)


class FBSPostingsProducts(Base):
    __tablename__ = "fbs_postings_products"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False, primary_key=True)
    name = sa.Column(sa.String(500))
    quantity = sa.Column(sa.Integer, nullable=False)
    offer_id = sa.Column(sa.String(100))
    price = sa.Column(sa.Integer, nullable=False)


class FBSPostingsProductsMandatoryMarks(Base):
    __tablename__ = "fbs_postings_products_mandatory_marks"

    mandatory_mark = sa.Column(sa.String(), primary_key=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbs_postings_products.posting_number', 'fbs_postings_products.sku']
        ),
    )


class FBSPostingsPostingServices(Base):
    __tablename__ = "fbs_postings_posting_services"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False, primary_key=True)
    marketplace_service_item_fulfillment = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_pickup = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_pvz = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_sc = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_ff = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_direct_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_not_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_part_goods_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_after_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)


class FBSPostingsProductsFinData(Base):
    __tablename__ = "fbs_postings_products_findata"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False, primary_key=True)
    commission_amount = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    commission_percent = sa.Column(sa.Integer, nullable=False, default=0)
    payout = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    old_price = sa.Column(sa.Integer, nullable=False)
    price = sa.Column(sa.Integer, nullable=False)
    total_discount_percent = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    total_discount_value = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    client_price = sa.Column(sa.Integer, nullable=True)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbs_postings_products.posting_number', 'fbs_postings_products.sku']
        ),
    )

class FBSPostingsProductsFinDataActions(Base):
    __tablename__ = "fbs_postings_products_findata_actions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False)
    sold_on_action = sa.Column(sa.String(255), nullable=False)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbs_postings_products_findata.posting_number', 'fbs_postings_products_findata.sku']
        ),
    )


class FBSPostingsProductsFinDataItemServices(Base):
    __tablename__ = "fbs_postings_products_findata_item_services"

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=False, primary_key=True)
    marketplace_service_item_fulfillment = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_pickup = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_pvz = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_sc = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_dropoff_ff = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_direct_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_flow_trans = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_not_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_part_goods_customer = sa.Column(sa.DECIMAL(12, 2), default=0)
    marketplace_service_item_return_after_deliv_to_customer = sa.Column(sa.DECIMAL(12, 2), default=0)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbs_postings_products_findata.posting_number', 'fbs_postings_products_findata.sku']
        ),
    )

# ---------------------------------------------------------------------------
class FBOReturns(Base):
    """ .... """
    __tablename__ = "fbo_postings_returns"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number),\
        nullable=False, primary_key=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False, primary_key=True)
    fbo_return_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    order_number = sa.Column(sa.String(50), nullable=False)
    last_posting_number = sa.Column(sa.String(50), nullable=False)
    quantity_returned = sa.Column(sa.Integer, nullable=False)
    accepted_from_customer_moment = sa.Column(sa.DateTime, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)
    current_place_name = sa.Column(sa.String(100), nullable=True)
    dst_place_name = sa.Column(sa.String(50), nullable=True)
    is_opened = sa.Column(sa.Boolean, nullable=False)
    return_reason_name = sa.Column(sa.String(100), nullable=True)
    returned_to_ozon_moment = sa.Column(sa.DateTime, nullable=True)
    status_name = sa.Column(sa.String(40), nullable=True)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbo_postings_products.posting_number', 'fbo_postings_products.sku']
        ),
    )
    

# ---------------------------------------------------------------------------
class FBSReturns(Base):
    """ .... """
    __tablename__ = "fbs_postings_returns"

    posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number),\
        nullable=False, primary_key=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    fbs_return_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    order_number = sa.Column(sa.String(50), nullable=False)
    last_posting_number = sa.Column(sa.String(50), nullable=False)
    quantity_returned = sa.Column(sa.Integer, nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)
    status = sa.Column(sa.String(155), nullable=False)
    is_moving = sa.Column(sa.Boolean, nullable=False)
    is_opened = sa.Column(sa.Boolean, nullable=False)
    last_free_waiting_day = sa.Column(sa.DateTime, nullable=True)
    place_id = sa.Column(sa.String(20), nullable=True)
    moving_to_place_name = sa.Column(sa.String(255), nullable=True)
    price = sa.Column(sa.Integer, nullable=False)
    price_without_commission = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    commission = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    commission_percent = sa.Column(sa.Integer, nullable=False)
    return_date = sa.Column(sa.DateTime, nullable=False)
    return_reason_name = sa.Column(sa.String(100), nullable=True)
    waiting_for_seller_date_time = sa.Column(sa.DateTime, nullable=True)
    returned_to_seller_date_time = sa.Column(sa.DateTime, nullable=True)
    waiting_for_seller_days = sa.Column(sa.Integer, nullable=True)
    returns_keeping_cost = sa.Column(sa.Integer, nullable=True)

    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['posting_number', 'sku'],
            ['fbs_postings_products.posting_number', 'fbs_postings_products.sku']
        ),
    )


# ---------------------------------------------------------------------------
class FinanceTransactions(Base):
    """financials """
    __tablename__ = 'finance_transactions'

    operation_id = sa.Column(sa.BIGINT, primary_key=True, unique=True, nullable=False)
    operation_type = sa.Column(sa.String(100), nullable=False)
    operation_date = sa.Column(sa.DateTime, nullable=False)
    operation_type_name = sa.Column(sa.String(100), nullable=False)
    delivery_charge = sa.Column(sa.DECIMAL(12, 2), default=0)
    return_delivery_charge = sa.Column(sa.DECIMAL(12, 2), default=0)
    accruals_for_sale = sa.Column(sa.DECIMAL(12, 2), default=0)
    sale_commission = sa.Column(sa.DECIMAL(12, 2), default=0)
    amount = sa.Column(sa.DECIMAL(12, 2), default=0)
    type = sa.Column(sa.Enum(FinancialTransactionTypeEnum), nullable=False)
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)


class FinanceTransactionsOperationPosting(Base):
    """financials """
    __tablename__ = 'finance_transactions_operation_posting'

    operation_id = sa.Column(sa.BIGINT, sa.ForeignKey(FinanceTransactions.operation_id), primary_key=True, unique=True, nullable=False)
    delivery_schema = sa.Column(sa.Enum(FinancialDeliverySchemaEnum), nullable=False)
    order_date = sa.Column(sa.DateTime, nullable=False)
    fbo_posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBOPostings.posting_number), nullable=True)
    fbs_posting_number = sa.Column(sa.String(50), sa.ForeignKey(FBSPostings.posting_number), nullable=True)
    warehouse_id = sa.Column(sa.BIGINT, nullable=False)                 # TODO : think of a relation with warehouses for further logistics cost calculation!


class FinanceTransactionsOperationItems(Base):
    """Items of a transaction, if a transaction is a type of 'orders' then it usually contains skus from the order itself, otherwise some
    description of a service transaction"""
    __tablename__ = 'finance_transactions_operation_items'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    operation_id = sa.Column(sa.BIGINT, sa.ForeignKey(FinanceTransactions.operation_id), nullable=False)
    name = sa.Column(sa.String(500), nullable=True)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=True)


class FinanceTransactionsOperationServices(Base):
    """Services incurred for a given operation in finance transactions, major assumption is that a transaction that has
    full 'services' field is either of a type 'orders' or 'returns'."""
    __tablename__ = 'finance_transactions_operation_services'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    operation_id = sa.Column(sa.BIGINT, sa.ForeignKey(FinanceTransactionsOperationPosting.operation_id), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    price = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)


class AnalyticsItemTurnover(Base):
    """An entity for incurred storage fees and turnover metrics at FBO warehouses.
    Has periods and categories to filter, contains periods of half a month's"""
    __tablename__ = 'analytics_item_turnover'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    period = sa.Column(sa.String(25), nullable=False)
    category_id = sa.Column(sa.Integer, nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    discounted = sa.Column(sa.Boolean, nullable=False)
    turnover = sa.Column(sa.Integer, nullable=True)
    threshold_free = sa.Column(sa.Integer, nullable=True)
    avg_sold_items = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    avg_stock_items = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    avg_stock_items_free = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    item_commission_part = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    last_updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class AnalyticsData(Base):
    """An entity for analytical data from OZON such as hits, conversion rate, ad costs and etc."""
    __tablename__ = 'analytics_data'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    date_ = sa.Column(sa.Date, nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    hits_tocart_search = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    hits_tocart_pdp = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    hits_tocart = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    conv_tocart_search = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    conv_tocart_pdp = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    conv_tocart = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    adv_view_pdp = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    adv_view_search_category = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    adv_view_all = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    adv_sum_all = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    position_category = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)


class AnalyticsStockOnWarehouses(Base):
    """For FBO stock on warehouses"""
    __tablename__ = 'analytics_stock_on_warehouses'

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())
    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    warehouse_name = sa.Column(sa.String(100), nullable=False)
    item_code = sa.Column(sa.String(55), nullable=False)
    item_name = sa.Column(sa.Text, nullable=False)
    promised_amount = sa.Column(sa.Integer, nullable=False)
    free_to_sell_amount = sa.Column(sa.Integer, nullable=False)
    reserved_amount = sa.Column(sa.Integer, nullable=False)


class Campaigns(Base):
    """For Ad campaigns"""
    __tablename__ = 'campaigns'

    supplier_id = sa.Column(sa.Integer, sa.ForeignKey(Supplier.supplier_id), nullable=False)
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    title = sa.Column(sa.String(100), nullable=False)
    state = sa.Column(sa.Enum(CampaignStateEnum), nullable=False)
    adv_object_type = sa.Column(sa.Enum(AdvObjectTypeEnum), nullable=False)
    from_date = sa.Column(sa.Date, nullable=False)
    to_date = sa.Column(sa.Date, nullable=True)
    budget = sa.Column(sa.Integer, nullable=False, default=0)
    daily_budget = sa.Column(sa.Integer, nullable=False, default=0)
    created_at = sa.Column(sa.Date, nullable=False)
    updated_at = sa.Column(sa.Date, nullable=False)


class CampaignPlacement(Base):
    """Placement variants for campaigns"""
    __tablename__ = 'campaign_placement'

    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), primary_key=True, nullable=False)
    placement = sa.Column(sa.Enum(ProductCampaignPlacementEnum), primary_key=True, nullable=False)


class CampaignObjects(Base):
    """campaign objects, it may be a product sku or an ad object, it depends on of what object type the campaign is"""
    __tablename__ = 'campaign_objects'

    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), primary_key=True, nullable=False)
    ad_object = sa.Column(sa.Integer, primary_key=True, nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=True)


class CampaignProducts(Base):
    """campaign products, fetches bids, phrases (their bids and relevance) and stop words.
    Applies to SKU campaigns"""
    __tablename__ = 'campaign_products'

    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), primary_key=True, unique=True, nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), primary_key=True, unique=True, nullable=False)
    bid = sa.Column(sa.Integer, nullable=False)
    group_id = sa.Column(sa.Integer, nullable=True)


class CampaignProductPhrases(Base):
    """campaign products' phrases and their bid + relevance"""
    __tablename__ = 'campaign_product_phrases'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    campaign_id = sa.Column(sa.Integer, nullable=False)
    sku = sa.Column(sa.Integer, nullable=False)
    phrase = sa.Column(sa.String(100), nullable=False)
    bid = sa.Column(sa.Integer, nullable=False)
    relevance_status = sa.Column(sa.Enum(PerfSearchBidRelevanceEnum), nullable=False)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['campaign_id', 'sku'],
            ['campaign_products.campaign_id', 'campaign_products.sku']
        ),
    )


class CampaignProductStopWords(Base):
    """campaign products' stop words"""
    __tablename__ = 'campaign_product_stop_words'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    campaign_id = sa.Column(sa.Integer, nullable=False)
    sku = sa.Column(sa.Integer, nullable=False)
    stop_word = sa.Column(sa.String(100), nullable=False)
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ['campaign_id', 'sku'],
            ['campaign_products.campaign_id', 'campaign_products.sku']
        ),
    )


class CampaignSearchPromoProducts(Base):
    """campaign products, fetches bids, phrases (their bids and relevance) and stop words.
    Applies to SKU campaigns"""
    __tablename__ = 'campaign_search_promo_products'

    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), primary_key=True, unique=True, nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), primary_key=True, unique=True, nullable=False)
    bid = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    bid_price = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    previous_week_views = sa.Column(sa.Integer, nullable=True, default=0)
    this_week_views = sa.Column(sa.Integer, nullable=True, default=0)
    visibility_index = sa.Column(sa.Integer, nullable=False, default=0)
    prev_visibility_index = sa.Column(sa.Integer, nullable=False, default=0)


class CampaignProductStatistics(Base):
    """default statistics report for any type of a campaign, but it has different layout"""
    __tablename__ = 'campaign_product_statistics'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    placement_type = sa.Column(sa.String(55), nullable=True)
    phrase = sa.Column(sa.String(55), nullable=True)
    impressions = sa.Column(sa.Integer, nullable=False, default=0)
    clicks = sa.Column(sa.Integer, nullable=False, default=0)
    ctr = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    avg_bid = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    spent = sa.Column(sa.DECIMAL(12, 3), nullable=False, default=0)
    orders = sa.Column(sa.Integer, nullable=False, default=0)
    revenue = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    date_ = sa.Column(sa.Date, nullable=False)


class CampaignSearchPromoStatistics(Base):
    """default statistics report for any type of a campaign, but it has different layout"""
    __tablename__ = 'campaign_search_promo_statistics'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), nullable=False)
    sku = sa.Column(sa.Integer, sa.ForeignKey(ProductSource.sku), nullable=False)
    order_number = sa.Column(sa.String(100), nullable=False)
    search_bid = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    spent = sa.Column(sa.DECIMAL(12, 3), nullable=False, default=0)
    orders = sa.Column(sa.Integer, nullable=False, default=0)
    revenue = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    date_ = sa.Column(sa.Date, nullable=False)


class CampaignProductStatisticsCorrection(Base):
    """default statistics report for any type of a campaign, but it has different layout"""
    __tablename__ = 'campaign_stats_corrections'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    campaign_id = sa.Column(sa.Integer, sa.ForeignKey(Campaigns.id), nullable=False)
    correction = sa.Column(sa.DECIMAL(12, 3), nullable=False, default=0)
    date_ = sa.Column(sa.Date, nullable=False)


class LocalMapping(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'local_mapping'

    product_id = sa.Column(sa.Integer, sa.ForeignKey(Product.product_id, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, unique=True, nullable=False)
    sku_id = sa.Column(sa.String(155), sa.ForeignKey('staging_local.general_skus.sku_id', ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=True)
    note = sa.Column(sa.String(55), nullable=True)