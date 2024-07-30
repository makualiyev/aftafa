from enum import Enum
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as pg_UUID
from sqlalchemy.sql import func
import sqlalchemy as sa
from pydantic import BaseModel, constr

from aftafa.client.moysklad import schemas as sc
from aftafa.common.dal import postgres_url as db_url


Base = declarative_base()
engine = sa.create_engine(db_url)
session = Session(engine)


class CompanyTypeEnum(str, Enum):
    """Enum for counterparty field"""

    LEGAL = "legal"
    ENTREPRENEUR = "entrepreneur"
    INDIVIDUAL = "individual"


class ContractTypeEnum(str, Enum):
    """Enum for contract field"""

    COMMISSION = "Commission"
    SALES = "Sales"


class ContractRewardEnum(str, Enum):
    """Enum for contract field"""

    PERCENT_OF_SALES = "PercentOfSales"
    NONE = "None"


class StateTypeEnum(str, Enum):
    """Enum for state field"""

    REGULAR = "Regular"
    SUCCESSFUL = "Successful"
    UNSUCCESSFUL = "Unsuccessful"


class Account(Base):
    __tablename__ = "account"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    name = sa.Column(sa.String(55), nullable=False)


class AccountModel(BaseModel):
    id: UUID
    name: constr(max_length=55)

    class Config:
        orm_mode = True


class Group(Base):
    __tablename__ = "group"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )

    name = sa.Column(sa.String(55), nullable=False)
    index = sa.Column(sa.Integer, nullable=True)


class Employee(Base):
    __tablename__ = "employee"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    archived = sa.Column(sa.Boolean, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False)
    external_code = sa.Column(sa.String(255), nullable=False)
    uid = sa.Column(sa.String(255), nullable=True)


class Store(Base):
    """
    Склады
    По данной сущности можно осуществлять контекстный поиск с помощью специального параметра search.
    """

    __tablename__ = "store"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)
    # parent_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey('store.id'), nullable=True)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(
        sa.String(255), nullable=True
    )  # FIXME: change to non-nullable type
    external_code = sa.Column(sa.String(255), nullable=False)
    path_name = sa.Column(sa.String, nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False)
    updated = sa.Column(sa.DateTime, nullable=False)

    # children = relationship("Child")


class Counterparty(Base):
    """
    Средствами JSON API можно создавать и обновлять сведения о Контрагентах,
    запрашивать списки Контрагентов и сведения по отдельным Контрагентам.
    Счетами Контрагента и его контактными лицами можно управлять как в составе отдельного
    Контрагента, так и отдельно - с помощью специальных ресурсов для управления счетами и
    контактными лицами Контрагента. Кодом сущности для Контрагента в составе JSON API
    является ключевое слово counterparty.
    """

    __tablename__ = "counterparty"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    company_type = sa.Column(sa.Enum(CompanyTypeEnum), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False)


class Organization(Base):
    """
    С помощью специального ресурса можно управлять счетами отдельного юрлица. Кодом сущности
    для юрлица в составе JSON API является ключевое слово organization.
    """

    __tablename__ = "organization"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    company_type = sa.Column(sa.Enum(CompanyTypeEnum), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False)


class Contract(Base):
    """
    Кодом сущности для Договора в составе JSON API является ключевое слово contract
    """

    __tablename__ = "contract"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)
    agent_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Counterparty.id), nullable=False
    )
    owner_agent_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Organization.id), nullable=False
    )

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(
        sa.String(255), nullable=True
    )  # FIXME: change to non-nullable type
    external_code = sa.Column(sa.String(255), nullable=False)
    contract_type = sa.Column(sa.Enum(ContractTypeEnum), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    moment = sa.Column(sa.DateTime, nullable=False)
    reward_percent = sa.Column(sa.Integer, nullable=True)
    reward_type = sa.Column(sa.Enum(ContractRewardEnum))
    archived = sa.Column(sa.Boolean, nullable=False)


class Project(Base):
    """
    Кодом сущности для Проекта в составе JSON API является ключевое слово project
    """

    __tablename__ = "project"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False)
    created = sa.Column(sa.DateTime, nullable=False)


class DocumentState(Base):
    """
    states for customer order entities
    """

    __tablename__ = "document_state"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )

    name = sa.Column(sa.String(255), nullable=False)
    color = sa.Column(sa.String(255), nullable=False)
    entity_type = sa.Column(sa.String(255), nullable=False)
    state_type = sa.Column(sa.Enum(StateTypeEnum), nullable=False)


class CustomEntity(Base):
    """
    Пользовательский справочник
    """

    __tablename__ = "customentity"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    create_shared = sa.Column(sa.Boolean, nullable=False)


class CustomEntityMember(Base):
    """
    Элементы пользовательского справочника
    """

    __tablename__ = "customentity_member"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    custom_entity_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(CustomEntity.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)


class EntityAttribute(Base):
    """
    attributes for entities
    """

    __tablename__ = "attribute"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    custom_entity_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(CustomEntity.id), nullable=True
    )

    name = sa.Column(sa.String(255), nullable=False)
    required = sa.Column(sa.Boolean, nullable=False)
    show = sa.Column(sa.Boolean, nullable=False)
    description = sa.Column(sa.String(4096), nullable=True)
    entity_type = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.Enum(sc.AttributeTypeEnum), nullable=False)


class SalesChannel(Base):
    """
    Кодом сущности для Канала продаж в составе JSON API является ключевое слово saleschannel.
    """

    __tablename__ = "saleschannel"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(pg_UUID(as_uuid=True), sa.ForeignKey(Group.id), nullable=False)

    name = sa.Column(sa.String(255), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    type = sa.Column(sa.Enum(sc.SalesChannelEnum), nullable=False)
    archived = sa.Column(sa.Boolean, nullable=False)


class ProductFolder(Base):
    __tablename__ = "product_folder"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Account.id), nullable=False
    )
    group_id = sa.Column(
        pg_UUID(as_uuid=True), sa.ForeignKey(Group.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    parent_product_folder_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey('moysklad.product_folder.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )

    name = sa.Column(sa.String(55), nullable=False)
    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    path_name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(4096), nullable=True)
    effective_vat = sa.Column(sa.Integer, nullable=True)
    effective_vat_enabled = sa.Column(sa.Boolean, nullable=True)
    shared = sa.Column(sa.Boolean)
    tax_system = sa.Column(sa.Enum(sc.TaxSystemEnum), nullable=True)
    updated = sa.Column(sa.DateTime)
    use_parent_vat = sa.Column(sa.Boolean, nullable=True)
    vat = sa.Column(sa.Integer, nullable=True)
    vat_enabled = sa.Column(sa.Boolean, nullable=True)
    archived = sa.Column(sa.Boolean, nullable=False, default=False)

class Product(Base):
    __tablename__ = "product"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(pg_UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    account_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(Account.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    group_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(Group.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    product_folder_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(ProductFolder.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    supplier_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(Counterparty.id, ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True
    )
    name = sa.Column(sa.String(255), nullable=False)
    article = sa.Column(sa.String(255), nullable=True)

    code = sa.Column(sa.String(255), nullable=True)
    external_code = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(4096), nullable=True)
    path_name = sa.Column(sa.String(255), nullable=False)
    archived = sa.Column(sa.Boolean, nullable=False, default=False)
    shared = sa.Column(sa.Boolean)
    updated = sa.Column(sa.DateTime)

    volume = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    weight = sa.Column(sa.DECIMAL(12, 2), nullable=False, default=0)
    tnved = sa.Column(sa.String(255), nullable=True)
    variants_count = sa.Column(sa.Integer, nullable=True)
    tracking_type = sa.Column(sa.Enum(sc.TrackingTypeEnum), nullable=True)
    payment_item_type = sa.Column(sa.Enum(sc.PaymentItemTypeEnum), nullable=True)
    tax_system = sa.Column(sa.Enum(sc.TaxSystemEnum), nullable=True)
    use_parent_vat = sa.Column(sa.Boolean, nullable=True)
    vat = sa.Column(sa.Integer, nullable=True)
    vat_enabled = sa.Column(sa.Boolean, nullable=True)
    effective_vat = sa.Column(sa.Integer, nullable=True)
    effective_vat_enabled = sa.Column(sa.Boolean, nullable=True)


class ProductBarcode(Base):
    __tablename__ = "product_barcode"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    product_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(Product.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    
    barcode_type = sa.Column(sa.String(55), nullable=False)
    barcode = sa.Column(sa.String(100), nullable=False)


# class ProductPrice(Base):
#     __tablename__ = "product_price"
#     __table_args__ = {"schema": "moysklad"}

#     id = sa.Column(sa.Integer, primary_key=True, nullable=False)
#     product_id = sa.Column(
#         pg_UUID(as_uuid=True),
#         sa.ForeignKey(Product.id, ondelete="CASCADE", onupdate="CASCADE"),
#         nullable=False,
#     )

#     price = sa.Column()


class ProductAttribute(Base):
    __tablename__ = "product_attribute"
    __table_args__ = {"schema": "moysklad"}

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    product_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(Product.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    attribute_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(EntityAttribute.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    custom_entity_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(CustomEntity.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True
    )
    custom_entity_member_id = sa.Column(
        pg_UUID(as_uuid=True),
        sa.ForeignKey(CustomEntityMember.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True
    )

    value = sa.Column(sa.String(255), nullable=False)

    
