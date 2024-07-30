import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.dialects.postgresql import UUID as pg_UUID
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.sql import func


from aftafa.client.ec.schemas import (
    UomEnum,
    InventoryRecordMovementTypeEnum,
    NomenclatureTypeEnum,
    VatTypeEnum,
    LegalTypeEnum,
    CurrencyEnum
)

from aftafa.client.ec.db import Base, DEFAULT_SCHEMA


class Server(Base):
    """
    
    """
    __tablename__ = "server"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), unique=True, nullable=False)


class Nomenclature(Base):
    """
    """
    __tablename__ = "nomenclature"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    ec_code = sa.Column(sa.String(50), nullable=False, primary_key=True, unique=True)
    bitrix_code = sa.Column(sa.String(100), nullable=True, index=True)

    name = sa.Column(sa.String(255), nullable=False)
    sku = sa.Column(sa.String(100), nullable=True)
    brand = sa.Column(sa.String(100), nullable=True)
    type = sa.Column(sa.String(25), nullable=False)
    group = sa.Column(sa.String(100), nullable=True)
    vat = sa.Column(sa.String(25), nullable=True)
    barcode = sa.Column(sa.String(25), nullable=True)
    weight = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    volume = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    author = sa.Column(sa.String(100), nullable=True)
    created_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())


class RawPriceList(Base):
    __tablename__ = "raw_price_list"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    ec_code = sa.Column(sa.String(50), sa.ForeignKey(Nomenclature.ec_code, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    is_active = sa.Column(sa.String(15), nullable=True)
    price_type = sa.Column(sa.String(50), nullable=False)
    period = sa.Column(sa.Date, nullable=False)
    period_end = sa.Column(sa.Date, nullable=False)
    data_ = sa.Column(sa.String(200), nullable=True)
    comment = sa.Column(sa.String(200), nullable=True)
    currency = sa.Column(sa.String(25), nullable=False)
    price = sa.Column(sa.DECIMAL(12, 2), nullable=False)

    updated_at = sa.Column(sa.Date, nullable=False, default=sa.func.now())
    

class SimrusMailListStocks(Base):
    __tablename__ = "simrus_mail_list_stocks"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    barcode = sa.Column(sa.String(50), nullable=True)
    name = sa.Column(sa.String(150), nullable=True)
    sku = sa.Column(sa.String(50), nullable=True)
    add_code = sa.Column(sa.String(50), nullable=True)
    weight = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    volume = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    status = sa.Column(sa.String(100), nullable=True)
    warehouse = sa.Column(sa.String(200), nullable=False)
    stock_type = sa.Column(sa.String(50), nullable=False)

    price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=False)

    report_timestamp = sa.Column(sa.TIMESTAMP, nullable=False)
    updated_at = sa.Column(sa.TIMESTAMP, nullable=False, default=sa.func.now())


class SchaubMailListStocks(Base):
    __tablename__ = "schaub_mail_list_stocks"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    name = sa.Column(sa.String(255), nullable=True)
    nomenclature_type = sa.Column(sa.String(255), nullable=True)
    sku = sa.Column(sa.String(155), nullable=True)
    uom = sa.Column(sa.String(55), nullable=True)
    
    warehouse = sa.Column(sa.String(200), nullable=False)
    stock_type = sa.Column(sa.String(50), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)

    report_type = sa.Column(sa.String(25), nullable=False)
    report_date = sa.Column(sa.Date, nullable=False)
    extracted_at = sa.Column(sa.TIMESTAMP, nullable=False)


class LocalMapping(Base):
    """
    Default mapping for local base SKUs' mapping from different schemas.
    """
    __tablename__ = 'local_mapping'
    __table_args__ = {'schema': DEFAULT_SCHEMA}

    ec_code = sa.Column(sa.String(50), sa.ForeignKey(Nomenclature.ec_code, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, unique=True, index=True, nullable=False)
    sku_id = sa.Column(sa.String(155), sa.ForeignKey('staging_local.general_skus.sku_id', ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=True)
    note = sa.Column(sa.String(55), nullable=True)

    updated_at = sa.Column(sa.DateTime, default=sa.func.now())


# class Collection(Base):
#     """
#     """
#     __tablename__ = "collection"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
#     name = sa.Column(sa.String(255), nullable=False)


# class Organization(Base):
#     """
#     """
#     __tablename__ = "legal_name"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     # collection_id = sa.Column(sa.Integer, sa.ForeignKey(Collection.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

#     name = sa.Column(sa.String(255), nullable=False)


# class CounterParty(Base):
#     """
#     """
#     __tablename__ = "counterparty"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     ut_code = sa.Column(sa.String(50), nullable=False, index=True)

#     name = sa.Column(sa.String(255), nullable=False)
#     legal_type = sa.Column(sa.Enum(LegalTypeEnum), nullable=False)
#     is_supplier = sa.Column(sa.Boolean, nullable=False)


# class Warehouse(Base):
#     """
#     """
#     __tablename__ = "warehouse"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
#     name = sa.Column(sa.String(255), nullable=False)


# class Nomenclature(Base):
#     """
#     """
#     __tablename__ = "nomenclature"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     ec_code = sa.Column(sa.String(50), nullable=False, index=True)
#     bitrix_code = sa.Column(sa.BIGINT, nullable=True, index=True)

#     name = sa.Column(sa.String(255), nullable=False)
#     sku = sa.Column(sa.String(100), nullable=True)
#     uom = sa.Column(sa.Enum(UomEnum), nullable=False)
#     type = sa.Column(sa.Enum(NomenclatureTypeEnum), nullable=True)
#     vat = sa.Column(sa.Enum(VatTypeEnum), nullable=True)


# class DocIncome(Base):
#     """
#     """
#     __tablename__ = "doc_income"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
#     server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     counterparty_id = sa.Column(sa.Integer, sa.ForeignKey(CounterParty.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     warehouse_id = sa.Column(sa.Integer, sa.ForeignKey(Warehouse.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
#     ut_code = sa.Column(sa.String(50), nullable=False, index=True)

#     date = sa.Column(sa.DateTime, nullable=False)
#     income_corr_id = sa.Column(sa.String(50), nullable=True)                                        # Номер входящего документа
#     currency = sa.Column(sa.Enum(CurrencyEnum), nullable=False)

class InventoryRegistry(Base):
    """
    """
    __tablename__ = "inventory_registry"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    registry_record_hash = sa.Column(sa.String(32), unique=True, nullable=False)

    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    movement_type = sa.Column(sa.Enum(InventoryRecordMovementTypeEnum), nullable=False)
    stock_control = sa.Column(sa.Boolean, nullable=False)
    is_storno = sa.Column(sa.Boolean, nullable=False)
    period = sa.Column(sa.DateTime, nullable=False)
    warehouse = sa.Column(sa.String(155), nullable=False)
    registry = sa.Column(sa.String(255), nullable=False)
    registry_document_type = sa.Column(sa.String(155), nullable=True)
    registry_operation = sa.Column(sa.String(155), nullable=True)
    registry_document_guid = sa.Column(sa.String(36), nullable=True)
    registry_document_number = sa.Column(sa.String(55), nullable=False)
    registry_document_date = sa.Column(sa.DateTime, nullable=False)
    client_code = sa.Column(sa.String(55), nullable=True)
    client = sa.Column(sa.String(255), nullable=True)
    warehouse_sender = sa.Column(sa.String(155), nullable=True)
    warehouse_receiver = sa.Column(sa.String(155), nullable=True)
    ec_row_number = sa.Column(sa.Integer, nullable=True)
    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    product_name = sa.Column(sa.String(200), nullable=False)
    quantity = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    
    meta_created_at = sa.Column(sa.DateTime, nullable=False)
    meta_is_valid = sa.Column(sa.Boolean, nullable=False)
    meta_valid_from = sa.Column(sa.DateTime, nullable=True)
    meta_valid_to = sa.Column(sa.DateTime, nullable=True)
   
   
class PurchaseDocumentGoods(Base):
    """
    """
    __tablename__ = "purchase_document_goods"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_id = sa.Column(sa.String(32), nullable=False)
    document_row_id = sa.Column(sa.String(32), unique=True, nullable=False)
    ec_row_id = sa.Column(sa.String(36), nullable=False)

    supplier_code = sa.Column(sa.String(55), nullable=False)
    supplier = sa.Column(sa.String(155), nullable=False)
    warehouse = sa.Column(sa.String(155), nullable=False)
    document_number = sa.Column(sa.String(55), nullable=False)
    document_date = sa.Column(sa.DateTime, nullable=False)
    document_currency = sa.Column(sa.String(55), nullable=False)
    document_vat_included_price = sa.Column(sa.String(55), nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    business_operation = sa.Column(sa.String(155), nullable=False)
    operation_tax_mode = sa.Column(sa.String(155), nullable=False)
    expense_accounted = sa.Column(sa.Boolean, nullable=False, default=False)
    expense_item = sa.Column(sa.String(155), nullable=True)
    incoming_document_number = sa.Column(sa.String(155), nullable=True)
    incoming_document_date = sa.Column(sa.String(155), nullable=True)
    incoming_document = sa.Column(sa.String(155), nullable=True)

    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    product_name = sa.Column(sa.String(150), nullable=False)
    vat_type = sa.Column(sa.String(50), nullable=False)
    price_type = sa.Column(sa.String(100), nullable=True)
    gtd_number = sa.Column(sa.String(255), nullable=True)

    package_quantity = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    quantity_RNPT = sa.Column(sa.Integer, nullable=True)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum_with_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    
    updated_at = sa.Column(sa.DateTime, default=sa.func.now())


class PurchaseDocuments(Base):
    """
    """
    __tablename__ = "purchase_documents"
    __table_args__ = (
            sa.UniqueConstraint(
                'ec_row_id',
                'data_version'
            ),
            {
            "schema": DEFAULT_SCHEMA,
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_guid = sa.Column(sa.String(36), nullable=False)
    ec_row_id = sa.Column(sa.String(36), nullable=False)
    data_version = sa.Column(sa.String(12), nullable=False)

    organization = sa.Column(sa.String(100), nullable=False)
    business_operation = sa.Column(sa.String(155), nullable=False)
    manager = sa.Column(sa.String(55), nullable=True)
    supplier_code = sa.Column(sa.String(55), nullable=False)
    supplier = sa.Column(sa.String(155), nullable=False)
    warehouse = sa.Column(sa.String(155), nullable=False)
    document_number = sa.Column(sa.String(55), nullable=False)
    document_date = sa.Column(sa.DateTime, nullable=False)
    document_currency = sa.Column(sa.String(55), nullable=False)
    document_vat_included_price = sa.Column(sa.Boolean, nullable=False)
    
    operation_tax_mode = sa.Column(sa.String(155), nullable=False)
    expense_accounted = sa.Column(sa.Boolean, nullable=False, default=False)
    expenses_analytics = sa.Column(sa.String(155), nullable=True)
    expense_item = sa.Column(sa.String(155), nullable=True)
    incoming_document_number = sa.Column(sa.String(155), nullable=True)
    incoming_document_date = sa.Column(sa.String(155), nullable=True)
    incoming_document = sa.Column(sa.String(155), nullable=True)

    document_row_no = sa.Column(sa.Integer, nullable=False)
    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    product_name = sa.Column(sa.String(150), nullable=False)
    vat_type = sa.Column(sa.String(50), nullable=False)
    price_type = sa.Column(sa.String(100), nullable=True)
    gtd_number = sa.Column(sa.String(255), nullable=True)

    package_quantity = sa.Column(sa.Integer, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    quantity_rnpt = sa.Column(sa.Integer, nullable=True)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_vat = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum_with_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_vat = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    
    meta_created_at = sa.Column(sa.DateTime, nullable=False)
    meta_is_valid = sa.Column(sa.Boolean, nullable=False)
    meta_valid_from = sa.Column(sa.DateTime, nullable=True)
    meta_valid_to = sa.Column(sa.DateTime, nullable=True)


class CustomerOrderDocuments(Base):
    """
    """
    __tablename__ = "customer_order_documents"
    __table_args__ = (
            sa.UniqueConstraint(
                'ec_row_id',
                'data_version'
            ),
            {
            "schema": DEFAULT_SCHEMA,
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_guid = sa.Column(sa.String(36), nullable=False)
    ec_row_id = sa.Column(sa.String(36), nullable=False)
    data_version = sa.Column(sa.String(12), nullable=False)

    organization = sa.Column(sa.String(100), nullable=False)
    business_operation = sa.Column(sa.String(155), nullable=False)
    manager = sa.Column(sa.String(55), nullable=True)
    document_status = sa.Column(sa.String(55), nullable=True)
    customer_order_status = sa.Column(sa.String(125), nullable=True)
    counterparty_type = sa.Column(sa.String(55), nullable=True)
    counterparty_legal_entity = sa.Column(sa.String(55), nullable=True)
    counterparty_code = sa.Column(sa.String(55), nullable=False)
    counterparty = sa.Column(sa.String(155), nullable=False)
    
    warehouse = sa.Column(sa.String(155), nullable=False)
    document_number = sa.Column(sa.String(55), nullable=False)
    document_date = sa.Column(sa.DateTime, nullable=False)
    document_vat_included_price = sa.Column(sa.Boolean, nullable=False)
    document_order_type = sa.Column(sa.String(120), nullable=True)
    shipment_date = sa.Column(sa.Date, nullable=True)
    
    customer_order_site = sa.Column(sa.String(125), nullable=True)
    store = sa.Column(sa.String(125), nullable=True)
    customer_order_order_number = sa.Column(sa.String(55), nullable=True)
    client_order_number = sa.Column(sa.String(55), nullable=True)
    
    document_comment = sa.Column(sa.Text, nullable=True)
    customer_order_comment = sa.Column(sa.Text, nullable=True)
    customer_order_client_comment = sa.Column(sa.Text, nullable=True)

    document_row_no = sa.Column(sa.Integer, nullable=False)
    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    
    vat_type = sa.Column(sa.String(50), nullable=False)
    price_type = sa.Column(sa.String(100), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_vat = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum_with_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    
    meta_created_at = sa.Column(sa.DateTime, nullable=False)
    meta_is_valid = sa.Column(sa.Boolean, nullable=False)
    meta_valid_from = sa.Column(sa.DateTime, nullable=True)
    meta_valid_to = sa.Column(sa.DateTime, nullable=True)
    
    
class RealizationDocuments(Base):
    """
    """
    __tablename__ = "realization_documents"
    __table_args__ = (
            sa.UniqueConstraint(
                'ec_row_id',
                'data_version'
            ),
            {
            "schema": DEFAULT_SCHEMA,
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_guid = sa.Column(sa.String(36), nullable=False)
    ec_row_id = sa.Column(sa.String(36), nullable=False)
    data_version = sa.Column(sa.String(12), nullable=False)

    organization = sa.Column(sa.String(100), nullable=False)
    business_operation = sa.Column(sa.String(155), nullable=False)
    manager = sa.Column(sa.String(55), nullable=True)
    shipment_status = sa.Column(sa.String(55), nullable=True)
    
    counterparty_type = sa.Column(sa.String(55), nullable=True)
    counterparty_legal_entity = sa.Column(sa.String(55), nullable=True)
    counterparty_code = sa.Column(sa.String(55), nullable=False)
    counterparty = sa.Column(sa.String(155), nullable=False)
    is_supplier = sa.Column(sa.Boolean, nullable=True)
    
    warehouse = sa.Column(sa.String(155), nullable=False)
    document_number = sa.Column(sa.String(55), nullable=False)
    document_date = sa.Column(sa.DateTime, nullable=False)
    document_vat_included_price = sa.Column(sa.Boolean, nullable=False)
    customer_order_order_number = sa.Column(sa.String(55), nullable=True)
    document_comment = sa.Column(sa.Text, nullable=True)
    
    related_order_guid = sa.Column(sa.String(36), nullable=False)
    related_order_date = sa.Column(sa.DateTime, nullable=False)
    related_order_number = sa.Column(sa.String(55), nullable=False)

    document_row_no = sa.Column(sa.Integer, nullable=False)
    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    
    vat_type = sa.Column(sa.String(50), nullable=False)
    price_type = sa.Column(sa.String(100), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_vat = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum_with_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    
    meta_created_at = sa.Column(sa.DateTime, nullable=False)
    meta_is_valid = sa.Column(sa.Boolean, nullable=False)
    meta_valid_from = sa.Column(sa.DateTime, nullable=True)
    meta_valid_to = sa.Column(sa.DateTime, nullable=True)


class ReturnFromClientDocuments(Base):
    """
    Документ Возврат от клиента
    """
    __tablename__ = "return_from_client_documents"
    __table_args__ = (
            sa.UniqueConstraint(
                'ec_row_id',
                'data_version'
            ),
            {
            "schema": DEFAULT_SCHEMA,
        },
        )

    id = sa.Column(sa.BIGINT, primary_key=True, autoincrement=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    document_guid = sa.Column(sa.String(36), nullable=False)
    ec_row_id = sa.Column(sa.String(36), nullable=False)
    data_version = sa.Column(sa.String(12), nullable=False)

    organization = sa.Column(sa.String(100), nullable=False)
    business_operation = sa.Column(sa.String(155), nullable=False)
    manager = sa.Column(sa.String(55), nullable=True)
    shipment_status = sa.Column(sa.String(55), nullable=True)
    
    counterparty_type = sa.Column(sa.String(55), nullable=True)
    counterparty_legal_entity = sa.Column(sa.String(55), nullable=True)
    counterparty_code = sa.Column(sa.String(55), nullable=False)
    counterparty = sa.Column(sa.String(155), nullable=False)
    is_supplier = sa.Column(sa.Boolean, nullable=True)
    
    warehouse = sa.Column(sa.String(155), nullable=False)
    document_number = sa.Column(sa.String(55), nullable=False)
    document_date = sa.Column(sa.DateTime, nullable=False)
    document_vat_included_price = sa.Column(sa.Boolean, nullable=False)
    customer_order_order_number = sa.Column(sa.String(55), nullable=True)
    document_comment = sa.Column(sa.Text, nullable=True)
    
    related_order_guid = sa.Column(sa.String(36), nullable=False)
    related_order_date = sa.Column(sa.DateTime, nullable=False)
    related_order_number = sa.Column(sa.String(55), nullable=False)

    document_row_no = sa.Column(sa.Integer, nullable=False)
    product_code = sa.Column(sa.String(50), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    
    vat_type = sa.Column(sa.String(50), nullable=False)
    price_type = sa.Column(sa.String(100), nullable=True)
    quantity = sa.Column(sa.Integer, nullable=False)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_vat = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum_with_vat = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    product_final_sum = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    
    meta_created_at = sa.Column(sa.DateTime, nullable=False)
    meta_is_valid = sa.Column(sa.Boolean, nullable=False)
    meta_valid_from = sa.Column(sa.DateTime, nullable=True)
    meta_valid_to = sa.Column(sa.DateTime, nullable=True)
    

class StockSnapshot(Base):
    """
    """
    __tablename__ = "stock_snapshot"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.String(32), primary_key=True)
    server_id = sa.Column(sa.Integer, sa.ForeignKey(Server.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    warehouse = sa.Column(sa.String(155), nullable=False)
    product_code = sa.Column(sa.String(50), sa.ForeignKey(Nomenclature.ec_code, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    product_sku = sa.Column(sa.String(150), nullable=True)
    
    shipping_stock = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    now_in_stock = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    now_reserved = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    now_available = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    incoming_stock = sa.Column(sa.DECIMAL(12, 2), nullable=False)
    available = sa.Column(sa.DECIMAL(12, 2), nullable=False)

    updated_at = sa.Column(sa.DateTime, default=sa.func.now())


class AlanSkladDocument(Base):
    """
    """
    __tablename__ = "alan_sklad_document"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    file_name = sa.Column(sa.String(155), nullable=False, index=True)
    file_checksum = sa.Column(sa.String(100), nullable=False)
    document_type = sa.Column(sa.String(25), nullable=False)
    document_number = sa.Column(sa.String(100), nullable=False)
    document_date = sa.Column(sa.String(100), nullable=False)
    document_page_count = sa.Column(sa.Integer, nullable=True)
    document_overall_quantity = sa.Column(sa.Integer, nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=True)


# class AlanSkladMX1Document(Base):
#     """
#     """
#     __tablename__ = "alan_sklad_mx1_document"
#     __table_args__ = {"schema": DEFAULT_SCHEMA}

#     id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
#     file_name = sa.Column(sa.String(155), nullable=False, index=True)
#     file_checksum = sa.Column(sa.String(100), nullable=False)

#     updated_at = sa.Column(sa.DateTime, nullable=True)


class AlanSkladMX3Document(Base):
    """
    """
    __tablename__ = "alan_sklad_mx3_document"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    file_id = sa.Column(sa.BigInteger, sa.ForeignKey(AlanSkladDocument.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    waybill_document_number = sa.Column(sa.String(155), nullable=True)
    waybill_number = sa.Column(sa.String(155), nullable=True)
    waybill_order_number = sa.Column(sa.String(155), nullable=True)
    waybill_document_index = sa.Column(sa.Integer, nullable=True)
    pp = sa.Column(sa.String(55), nullable=True)
    product_name = sa.Column(sa.String(255), nullable=True)
    product_code = sa.Column(sa.String(155), nullable=True)
    characteristics = sa.Column(sa.String(255), nullable=True)
    uom = sa.Column(sa.String(25), nullable=True)
    code_okei = sa.Column(sa.String(25), nullable=True)
    quantity = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    package_type = sa.Column(sa.String(155), nullable=True)
    quantity_package = sa.Column(sa.String(55), nullable=True)
    comment = sa.Column(sa.String(255), nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=True)


class AlanSkladMX1Document(Base):
    """
    """
    __tablename__ = "alan_sklad_mx1_document"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    file_id = sa.Column(sa.BigInteger, sa.ForeignKey(AlanSkladDocument.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    waybill_document_number = sa.Column(sa.String(155), nullable=True)
    waybill_number = sa.Column(sa.String(155), nullable=True)
    waybill_order_number = sa.Column(sa.String(155), nullable=True)
    waybill_document_index = sa.Column(sa.Integer, nullable=True)
    pp = sa.Column(sa.String(55), nullable=True)
    product_name = sa.Column(sa.String(255), nullable=True)
    product_code = sa.Column(sa.String(155), nullable=True)
    characteristics = sa.Column(sa.String(255), nullable=True)
    uom = sa.Column(sa.String(25), nullable=True)
    code_okei = sa.Column(sa.String(25), nullable=True)
    quantity = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_price = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    product_sum = sa.Column(sa.DECIMAL(12, 2), nullable=True)
    package_type = sa.Column(sa.String(155), nullable=True)
    quantity_package = sa.Column(sa.String(55), nullable=True)
    comment = sa.Column(sa.String(255), nullable=True)

    extracted_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=True)


class UserFileSupplyReport(Base):
    """
    """
    __tablename__ = "userfile_supply_report"
    __table_args__ = {"schema": DEFAULT_SCHEMA}

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    meta_filename = sa.Column(sa.String(255), nullable=False)
    meta_report_date = sa.Column(sa.String(255), nullable=False)
    meta_file_checksum = sa.Column(sa.String(255), nullable=False)

    project = sa.Column(sa.String(500), nullable=True)
    coutnry_origin = sa.Column(sa.String(500), nullable=True)
    manufacturer = sa.Column(sa.String(500), nullable=True)
    sku = sa.Column(sa.String(500), nullable=True)
    supplier = sa.Column(sa.String(500), nullable=True)
    photo = sa.Column(sa.String(500), nullable=True)
    category = sa.Column(sa.String(500), nullable=True)
    ec_name = sa.Column(sa.String(500), nullable=True)
    ec_bitrix_code = sa.Column(sa.String(500), nullable=True)
    tnved = sa.Column(sa.String(500), nullable=True)
    specification = sa.Column(sa.String(500), nullable=True)
    is_delvento_product = sa.Column(sa.String(500), nullable=True)
    ec_code = sa.Column(sa.String(500), nullable=True)
    barcode = sa.Column(sa.String(500), nullable=True)
    status_old = sa.Column(sa.String(500), nullable=True)
    status_new = sa.Column(sa.String(500), nullable=True)
    status_2 = sa.Column(sa.String(500), nullable=True)
    difference_plan_to_fact_pct = sa.Column(sa.String(500), nullable=True)
    fob_cost_usd = sa.Column(sa.String(500), nullable=True)
    ddp_n_cost_rub = sa.Column(sa.String(500), nullable=True)
    margin_s_pct = sa.Column(sa.String(500), nullable=True)
    ddp_d_cost_rub = sa.Column(sa.String(500), nullable=True)
    ec_delvento_a_cost_rub = sa.Column(sa.String(500), nullable=True)
    planned_cost_rub = sa.Column(sa.String(500), nullable=True)
    new_cost_rub = sa.Column(sa.String(500), nullable=True)
    new_wholesale_price_rub = sa.Column(sa.String(500), nullable=True)
    min_wholesale_price_rub = sa.Column(sa.String(500), nullable=True)
    rrp_23_new_price_rub = sa.Column(sa.String(500), nullable=True)
    promo_online_price_rub = sa.Column(sa.String(500), nullable=True)
    comment = sa.Column(sa.String(500), nullable=True)
    min_rrp_price_rub = sa.Column(sa.String(500), nullable=True)
    ozon_price_rub = sa.Column(sa.String(500), nullable=True)
    ozon_price_comment = sa.Column(sa.String(500), nullable=True)
    mvm_price_rub = sa.Column(sa.String(500), nullable=True)
    mvm_price_comment = sa.Column(sa.String(500), nullable=True)
    yandex_price_rub = sa.Column(sa.String(500), nullable=True)
    yandex_price_comment = sa.Column(sa.String(500), nullable=True)
    wildberries_price_rub = sa.Column(sa.String(500), nullable=True)
    wildberries_price_comment = sa.Column(sa.String(500), nullable=True)
    megamarket_price_rub = sa.Column(sa.String(500), nullable=True)
    megamarket_price_comment = sa.Column(sa.String(500), nullable=True)
    vs_price_rub = sa.Column(sa.String(500), nullable=True)
    vs_price_comment = sa.Column(sa.String(500), nullable=True)
    leroy_price_rub = sa.Column(sa.String(500), nullable=True)
        
    extracted_at = sa.Column(sa.DateTime, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=True)
