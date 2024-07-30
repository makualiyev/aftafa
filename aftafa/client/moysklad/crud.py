from sqlalchemy.orm.session import Session
from sqlalchemy.engine import Engine

from aftafa.client.moysklad.models import session, engine
import aftafa.client.moysklad.models as md
import aftafa.client.moysklad.schemas as sc


class DBWriter:
    def __init__(self, db_session: Session, db_engine: Engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def write_entity(self) -> None:
        """writes entities to the DB"""
        pass


# class GroupWriter(DBWriter):
#     def __init__(self, db_session: Session, db_engine: Engine) -> None:
#         super().__init__(db_session, db_engine)

#     def collect(self, )



class GroupDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.GroupEntity) -> md.Group:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Group.__dict__ if not i.startswith('_')]
        group_schema: sc.GroupEntity = schema_.dict(by_alias=False)
        group_schema = {key: value for key, value in group_schema.items() if key in req_fields}
        return md.Group(**group_schema)

    def check_integrity(self, group_model: md.Group) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        group_in_db: md.Group = session.query(md.Group).filter_by(id=group_model.id).first()
        if group_in_db:
            return True
        return False

    def update(self, group_model: md.Group) -> None:
        """Updates group entity"""
        group_in_db: md.Group = session.query(md.Group).filter_by(id=group_model.id).first()
        group_in_db.index = group_model.index
        group_in_db.name = group_model.name
        
        session.commit()

    def create(self, group_model: md.Group) -> None:
        """Creates group entity"""
        session.add(group_model)
        session.commit()


class EmployeeDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.EmployeeEntity) -> md.Employee:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Employee.__dict__ if not i.startswith('_')]
        empl_schema: sc.EmployeeEntity = schema_.dict(by_alias=False)
        empl_schema['group_id'] = empl_schema['group']['meta']['href'].split('/')[-1]
        empl_schema = {key: value for key, value in empl_schema.items() if key in req_fields}
        return md.Employee(**empl_schema)

    def check_integrity(self, empl_model: md.Employee) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        empl_in_db: md.Employee = session.query(md.Employee).filter_by(id=empl_model.id).first()
        if empl_in_db:
            return True
        return False

    def update(self, empl_model: md.Employee) -> None:
        """Updates employee entity"""
        empl_in_db: md.Employee = session.query(md.Employee).filter_by(id=empl_model.id).first()
        empl_in_db.group_id = empl_model.group_id
        empl_in_db.name = empl_model.name
        empl_in_db.archived = empl_model.archived
        empl_in_db.created = empl_model.created
        empl_in_db.uid = empl_model.uid
        
        session.commit()

    def create(self, empl_model: md.Employee) -> None:
        """Creates employee entity"""
        session.add(empl_model)
        session.commit()


class OrganizationDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.OrganizationEntity) -> md.Organization:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Organization.__dict__ if not i.startswith('_')]
        organization_schema: sc.OrganizationEntity = schema_.dict(by_alias=False)
        organization_schema['group_id'] = organization_schema['group']['meta']['href'].split('/')[-1]
        organization_schema = {key: value for key, value in organization_schema.items() if key in req_fields}
        return md.Organization(**organization_schema)

    def check_integrity(self, organization_model: md.Organization) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        organization_in_db: md.Organization = session.query(md.Organization).filter_by(id=organization_model.id).first()
        if organization_in_db:
            return True
        return False

    def update(self, organization_model: md.Organization) -> None:
        """Updates Store entity"""
        organization_in_db: md.Organization = session.query(md.Organization).filter_by(id=organization_model.id).first()
        organization_in_db.group_id = organization_model.group_id
        organization_in_db.name = organization_model.name
        organization_in_db.archived = organization_model.archived
        organization_in_db.description = organization_model.description
        organization_in_db.created = organization_model.created
        organization_in_db.code = organization_model.code
        organization_in_db.company_type = organization_model.company_type
        
        session.commit()

    def create(self, organization_model: md.Organization) -> None:
        """Creates Organization entity"""
        session.add(organization_model)
        session.commit()


class StoreDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.StoreEntity) -> md.Store:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Store.__dict__ if not i.startswith('_')]
        store_schema: sc.StoreEntity = schema_.dict(by_alias=False)
        store_schema['group_id'] = store_schema['group']['meta']['href'].split('/')[-1]
        store_schema = {key: value for key, value in store_schema.items() if key in req_fields}
        return md.Store(**store_schema)

    def check_integrity(self, store_model: md.Store) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        store_in_db: md.Store = session.query(md.Store).filter_by(id=store_model.id).first()
        if store_in_db:
            return True
        return False

    def update(self, store_model: md.Store) -> None:
        """Updates Store entity"""
        store_in_db: md.Store = session.query(md.Store).filter_by(id=store_model.id).first()
        store_in_db.group_id = store_model.group_id
        store_in_db.name = store_model.name
        store_in_db.archived = store_model.archived
        store_in_db.updated = store_model.updated
        store_in_db.path_name = store_model.path_name
        store_in_db.code = store_model.code
        
        session.commit()

    def create(self, store_model: md.Store) -> None:
        """Creates Store entity"""
        session.add(store_model)
        session.commit()

class CounterpartyDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.CounterpartyEntity) -> md.Counterparty:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Counterparty.__dict__ if not i.startswith('_')]
        counterparty_schema: sc.CounterpartyEntity = schema_.dict(by_alias=False)
        counterparty_schema['group_id'] = counterparty_schema['group']['meta']['href'].split('/')[-1]
        counterparty_schema = {key: value for key, value in counterparty_schema.items() if key in req_fields}
        return md.Counterparty(**counterparty_schema)

    def check_integrity(self, counterparty_model: md.Counterparty) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        counterparty_in_db: md.Counterparty = session.query(md.Counterparty).filter_by(id=counterparty_model.id).first()
        if counterparty_in_db:
            return True
        return False

    def update(self, counterparty_model: md.Counterparty) -> None:
        """Updates Counterparty entity"""
        counterparty_in_db: md.Counterparty = session.query(md.Counterparty).filter_by(id=counterparty_model.id).first()
        counterparty_in_db.group_id = counterparty_model.group_id
        counterparty_in_db.name = counterparty_model.name
        counterparty_in_db.code = counterparty_model.code
        counterparty_in_db.archived = counterparty_model.archived
        counterparty_in_db.description = counterparty_model.description
        counterparty_in_db.created = counterparty_model.created
        
        session.commit()

    def create(self, counterparty_model: md.Counterparty) -> None:
        """Creates Counterparty entity"""
        session.add(counterparty_model)
        session.commit()


class SalesChannelDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.SalesChannelEntity) -> md.SalesChannel:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.SalesChannel.__dict__ if not i.startswith('_')]
        saleschannel_schema: sc.SalesChannelEntity = schema_.dict(by_alias=False)
        saleschannel_schema['group_id'] = saleschannel_schema['group']['meta']['href'].split('/')[-1]
        saleschannel_schema = {key: value for key, value in saleschannel_schema.items() if key in req_fields}
        return md.SalesChannel(**saleschannel_schema)

    def check_integrity(self, saleschannel_model: md.SalesChannel) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        saleschannel_in_db: md.SalesChannel = session.query(md.SalesChannel).filter_by(id=saleschannel_model.id).first()
        if saleschannel_in_db:
            return True
        return False

    def update(self, saleschannel_model: md.SalesChannel) -> None:
        """Updates SalesChannel entity"""
        saleschannel_in_db: md.SalesChannel = session.query(md.SalesChannel).filter_by(id=saleschannel_model.id).first()
        saleschannel_in_db.group_id = saleschannel_model.group_id
        saleschannel_in_db.name = saleschannel_model.name
        saleschannel_in_db.code = saleschannel_model.code
        saleschannel_in_db.archived = saleschannel_model.archived
        saleschannel_in_db.description = saleschannel_model.description
        saleschannel_in_db.type = saleschannel_model.type
        
        session.commit()

    def create(self, saleschannel_model: md.SalesChannel) -> None:
        """Creates SalesChannel entity"""
        session.add(saleschannel_model)
        session.commit()


class DocumentStateDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.DocumentStateEntity) -> md.DocumentState:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.DocumentState.__dict__ if not i.startswith('_')]
        doc_state_schema: sc.DocumentStateEntity = schema_.dict(by_alias=False)
        doc_state_schema = {key: value for key, value in doc_state_schema.items() if key in req_fields}
        return md.DocumentState(**doc_state_schema)

    def check_integrity(self, doc_state_model: md.DocumentState) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        doc_state_in_db: md.DocumentState = session.query(md.DocumentState).filter_by(id=doc_state_model.id).first()
        if doc_state_in_db:
            return True
        return False

    def update(self, doc_state_model: md.DocumentState) -> None:
        """Updates Document State entity"""
        doc_state_in_db: md.DocumentState = session.query(md.DocumentState).filter_by(id=doc_state_model.id).first()
        doc_state_in_db.name = doc_state_model.name
        doc_state_in_db.color = doc_state_model.color
        doc_state_in_db.entity_type = doc_state_model.entity_type
        doc_state_in_db.state_type = doc_state_model.state_type
        
        session.commit()

    def create(self, doc_state_model: md.DocumentState) -> None:
        """Creates Document State entity"""
        session.add(doc_state_model)
        session.commit()


class ContractDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.ContractEntity) -> md.Contract:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Contract.__dict__ if not i.startswith('_')]
        contract_schema: sc.ContractEntity = schema_.dict(by_alias=False)
        contract_schema['group_id'] = contract_schema['group']['meta']['href'].split('/')[-1]
        contract_schema['agent_id'] = contract_schema['agent']['meta']['href'].split('/')[-1]
        contract_schema['owner_agent_id'] = contract_schema['own_agent']['meta']['href'].split('/')[-1]
        contract_schema = {key: value for key, value in contract_schema.items() if key in req_fields}
        return md.Contract(**contract_schema)

    def check_integrity(self, contract_model: md.Contract) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        contract_in_db: md.Contract = session.query(md.Contract).filter_by(id=contract_model.id).first()
        if contract_in_db:
            return True
        return False

    def update(self, contract_model: md.Contract) -> None:
        """Updates Contract entity"""
        contract_in_db: md.Contract = session.query(md.Contract).filter_by(id=contract_model.id).first()
        contract_in_db.name = contract_model.name
        contract_in_db.agent_id = contract_model.agent_id
        contract_in_db.owner_agent_id = contract_model.owner_agent_id
        contract_in_db.code = contract_model.code
        contract_in_db.contract_type = contract_model.contract_type
        contract_in_db.description = contract_model.description
        contract_in_db.moment = contract_model.moment
        contract_in_db.reward_percent = contract_model.reward_percent
        contract_in_db.reward_type = contract_model.reward_type
        contract_in_db.archived = contract_model.archived
        
        session.commit()

    def create(self, contract_model: md.Contract) -> None:
        """Creates Contract entity"""
        session.add(contract_model)
        session.commit()


class ProductFolderDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.ProductFolderEntity) -> md.ProductFolder:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.ProductFolder.__dict__ if not i.startswith('_')]
        prod_folder_schema: sc.ProductFolderEntity = schema_.dict(by_alias=False)
        prod_folder_schema['group_id'] = prod_folder_schema['group']['meta']['href'].split('/')[-1]
        # prod_folder_schema['agent_id'] = prod_folder_schema['agent']['meta']['href'].split('/')[-1]
        if prod_folder_schema.get('product_folder'):
            prod_folder_schema['parent_product_folder_id'] = prod_folder_schema['product_folder']['meta']['href'].split('/')[-1]
        prod_folder_schema = {key: value for key, value in prod_folder_schema.items() if key in req_fields}
        return md.ProductFolder(**prod_folder_schema)

    def check_integrity(self, product_folder_model: md.ProductFolder) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_folder_in_db: md.ProductFolder = session.query(md.ProductFolder).filter_by(id=product_folder_model.id).first()
        if prod_folder_in_db:
            return True
        return False

    def update(self, prod_folder_model: md.ProductFolder) -> None:
        """Updates ProductFolder entity"""
        prod_folder_in_db: md.ProductFolder = session.query(md.ProductFolder).filter_by(id=prod_folder_model.id).first()
        prod_folder_in_db.name = prod_folder_model.name
        prod_folder_in_db.group_id = prod_folder_model.group_id
        prod_folder_in_db.parent_product_folder_id = prod_folder_model.parent_product_folder_id
        prod_folder_in_db.code = prod_folder_model.code
        prod_folder_in_db.external_code = prod_folder_model.external_code 
        prod_folder_in_db.path_name = prod_folder_model.path_name 
        prod_folder_in_db.description = prod_folder_model.description 
        prod_folder_in_db.effective_vat = prod_folder_model.effective_vat 
        prod_folder_in_db.effective_vat_enabled = prod_folder_model.effective_vat_enabled 
        prod_folder_in_db.shared = prod_folder_model.shared 
        prod_folder_in_db.tax_system = prod_folder_model.tax_system 
        prod_folder_in_db.updated = prod_folder_model.updated 
        prod_folder_in_db.use_parent_vat = prod_folder_model.use_parent_vat 
        prod_folder_in_db.vat = prod_folder_model.vat 
        prod_folder_in_db.vat_enabled = prod_folder_model.vat_enabled 
        prod_folder_in_db.archived = prod_folder_model.archived
        
        session.commit()

    def create(self, prod_folder_model: md.ProductFolder) -> None:
        """Creates ProductFolder entity"""
        session.add(prod_folder_model)
        session.commit()


class ProductDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.ProductEntity) -> md.Product:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.Product.__dict__ if not i.startswith('_')]
        prod_schema: sc.ProductEntity = schema_.dict(by_alias=False)
        prod_schema['group_id'] = prod_schema['group']['meta']['href'].split('/')[-1]
        if prod_schema.get('product_folder'):
            prod_schema['product_folder_id'] = prod_schema['product_folder']['meta']['href'].split('/')[-1]

        if prod_schema.get('supplier'):
            prod_schema['supplier_id'] = prod_schema['supplier']['meta']['href'].split('/')[-1]
        prod_schema = {key: value for key, value in prod_schema.items() if key in req_fields}
        return md.Product(**prod_schema)

    def check_integrity(self, product_model: md.Product) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: md.Product = session.query(md.Product).filter_by(id=product_model.id).first()
        if prod_in_db:
            return True
        return False

    def update(self, product_model: md.Product) -> None:
        """Updates Product entity"""
        product_in_db: md.Product = session.query(md.Product).filter_by(id=product_model.id).first()
        product_in_db.name = product_model.name
        product_in_db.group_id = product_model.group_id
        product_in_db.product_folder_id = product_model.product_folder_id
        product_in_db.name = product_model.name
        product_in_db.article = product_model.article
        product_in_db.code = product_model.code
        product_in_db.external_code = product_model.external_code
        product_in_db.description = product_model.description
        product_in_db.path_name = product_model.path_name
        product_in_db.archived = product_model.archived
        product_in_db.shared = product_model.shared
        product_in_db.updated = product_model.updated
        product_in_db.volume = product_model.volume
        product_in_db.weight = product_model.weight
        product_in_db.tnved = product_model.tnved
        product_in_db.variants_count = product_model.variants_count
        product_in_db.tracking_type = product_model.tracking_type
        product_in_db.payment_item_type = product_model.payment_item_type
        product_in_db.tax_system = product_model.tax_system
        product_in_db.use_parent_vat = product_model.use_parent_vat
        product_in_db.vat = product_model.vat
        product_in_db.vat_enabled = product_model.vat_enabled
        product_in_db.effective_vat = product_model.effective_vat
        product_in_db.effective_vat_enabled = product_model.effective_vat_enabled
        
        session.commit()

    def create(self, product_model: md.Product) -> None:
        """Creates Product entity"""
        session.add(product_model)
        session.commit()

class ProductBarcodeDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.ProductEntity) -> md.ProductBarcode | bool:
        """prepares ORM model for a given schema"""
        prod_schema: sc.ProductEntity = schema_.dict(by_alias=False)
        prod_barcodes: list[md.ProductBarcode | None] = []

        if prod_schema_barcodes := prod_schema.get('barcodes'):
            for barcode_dict in prod_schema_barcodes:
                for barcode_type_, barcode_value_ in barcode_dict.items():
                    barcode_model: md.ProductBarcode = md.ProductBarcode(
                                        product_id=prod_schema['id'],
                                        barcode_type=barcode_type_,
                                        barcode=barcode_value_,
                                    )
                    prod_barcodes.append(barcode_model)

        return prod_barcodes

    def check_integrity(self, product_barcode_model: md.ProductBarcode) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: md.ProductBarcode = session.query(md.ProductBarcode).filter(
            md.ProductBarcode.product_id == product_barcode_model.product_id,
            md.ProductBarcode.barcode_type == product_barcode_model.barcode_type
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, product_barcode_model: md.ProductBarcode) -> None:
        """Updates Product barcodes entity"""
        product_barcode_in_db: md.ProductBarcode = session.query(md.ProductBarcode).filter(
            md.ProductBarcode.product_id == product_barcode_model.product_id,
            md.ProductBarcode.barcode_type == product_barcode_model.barcode_type
        ).first()
        product_barcode_in_db.barcode = product_barcode_model.barcode

        session.commit()

    def create(self, product_barcode_model: md.ProductBarcode) -> None:
        """Creates Product entity"""
        session.add(product_barcode_model)
        session.commit()


class ProductAttributeDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def prep_model(self, schema_: sc.ProductEntity) -> md.ProductAttribute | bool:
        """prepares ORM model for a given schema"""
        prod_schema: sc.ProductEntity = schema_.dict(by_alias=False)
        prod_attributes: list[md.ProductAttribute | None] = []

        if prod_schema_attributes := prod_schema.get('attributes'):
            for attribute_dict in prod_schema_attributes:
                attribute_model: md.ProductAttribute = md.ProductAttribute(
                                    product_id=prod_schema['id'],
                                    attribute_id=attribute_dict['meta']['href'].split('/')[-1]
                )
                
                if attribute_dict['type'].value == 'customentity':
                    attribute_model.custom_entity_id = attribute_dict['value']['meta']['href'].split('/')[-2]
                    attribute_model.custom_entity_member_id = attribute_dict['value']['meta']['href'].split('/')[-1]
                    customentity_member_in_db: md.CustomEntityMember = self.db_session.query(md.CustomEntityMember).filter(
                                                        md.CustomEntityMember.id == attribute_dict['value']['meta']['href'].split('/')[-1]
                                                    ).first()
                    attribute_model.value: str = customentity_member_in_db.name
                else:
                    attribute_model.value = attribute_dict['value']
                prod_attributes.append(attribute_model)

        return prod_attributes

    def check_integrity(self, product_attribute_model: md.ProductAttribute) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: md.ProductAttribute = session.query(md.ProductAttribute).filter(
            md.ProductAttribute.product_id == product_attribute_model.product_id,
            md.ProductAttribute.attribute_id == product_attribute_model.attribute_id,
            md.ProductAttribute.value == product_attribute_model.value
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, product_attribute_model: md.ProductAttribute) -> None:
        """Updates Product attributes entity"""
        prod_attr_in_db: md.ProductAttribute = session.query(md.ProductAttribute).filter(
            md.ProductAttribute.product_id == product_attribute_model.product_id,
            md.ProductAttribute.attribute_id == product_attribute_model.attribute_id,
            md.ProductAttribute.value == product_attribute_model.value
        ).first()
        prod_attr_in_db.attribute_id = product_attribute_model.attribute_id
        prod_attr_in_db.custom_entity_id = product_attribute_model.custom_entity_id
        prod_attr_in_db.custom_entity_member_id = product_attribute_model.custom_entity_member_id
        prod_attr_in_db.value = product_attribute_model.value

        session.commit()

    def create(self, product_attribute_model: md.ProductAttribute) -> None:
        """Creates Product attribute entity"""
        session.add(product_attribute_model)
        session.commit()


class EntityAttrDBWriter:
    def __init__(self, entity_type: str, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.entity_type = entity_type

    def prep_model(self, schema_: sc.Attribute, customentity_id: str = None) -> md.EntityAttribute:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.EntityAttribute.__dict__ if not i.startswith('_')]
        attribute_schema: sc.Attribute = schema_.dict(by_alias=False)
        attribute_schema['entity_type'] = self.entity_type
        if customentity_id:
            attribute_schema['custom_entity_id'] = customentity_id
        if not attribute_schema.get('show'):
            attribute_schema['show'] = True
        attribute_schema = {key: value for key, value in attribute_schema.items() if key in req_fields}
        return md.EntityAttribute(**attribute_schema)

    def check_integrity(self, attribute_model: md.EntityAttribute) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        attribute_in_db: md.EntityAttribute = session.query(md.EntityAttribute).filter_by(id=attribute_model.id).first()
        if attribute_in_db:
            return True
        return False

    def update(self, attribute_model: md.EntityAttribute) -> None:
        """Updates Contract entity"""
        attribute_in_db: md.EntityAttribute = session.query(md.EntityAttribute).filter_by(id=attribute_model.id).first()
        attribute_in_db.name = attribute_model.name
        attribute_in_db.description = attribute_model.description
        attribute_in_db.required = attribute_model.required
        attribute_in_db.show = attribute_model.show
        attribute_in_db.type = attribute_model.type

        try:
            assert attribute_in_db.entity_type == attribute_model.entity_type
        except AssertionError:
            print("something's fucked up")
        
        session.commit()

    def create(self, attribute_model: md.EntityAttribute) -> None:
        """Creates Contract entity"""
        session.add(attribute_model)
        session.commit()


class CustomEntityDBWriter:
    def __init__(self, customentity_id: str, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.customentity_id = customentity_id

    def prep_model(self, schema_: sc.CustomEntity) -> md.CustomEntity:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.CustomEntity.__dict__ if not i.startswith('_')]
        customentity_schema: sc.CustomEntity = schema_.dict(by_alias=False)
        customentity_schema['id'] = self.customentity_id 
        customentity_schema = {key: value for key, value in customentity_schema.items() if key in req_fields}
        return md.CustomEntity(**customentity_schema)

    def check_integrity(self, customentity_model: md.CustomEntity) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        customentity_in_db: md.CustomEntity = session.query(md.CustomEntity).filter_by(id=customentity_model.id).first()
        if customentity_in_db:
            return True
        return False

    def update(self, customentity_model: md.CustomEntity) -> None:
        """Updates Contract entity"""
        customentity_in_db: md.CustomEntity = session.query(md.CustomEntity).filter_by(id=customentity_model.id).first()
        customentity_in_db.name = customentity_model.name
        customentity_in_db.create_shared = customentity_model.create_shared
        
        session.commit()

    def create(self, customentity_model: md.CustomEntity) -> None:
        """Creates Contract entity"""
        session.add(customentity_model)
        session.commit()
        

class CustomEntityMemberDBWriter:
    def __init__(self, customentity_id: str, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.customentity_id = customentity_id

    def prep_model(self, schema_: sc.CustomEntityMember) -> md.CustomEntityMember:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in md.CustomEntityMember.__dict__ if not i.startswith('_')]
        customentity_member_schema: sc.CustomEntityMember = schema_.dict(by_alias=False)
        customentity_member_schema['custom_entity_id'] = self.customentity_id
        customentity_member_schema['group_id'] = customentity_member_schema['group']['meta']['href'].split('/')[-1]
        customentity_member_schema = {key: value for key, value in customentity_member_schema.items() if key in req_fields}
        return md.CustomEntityMember(**customentity_member_schema)

    def check_integrity(self, customentity_member_model: md.CustomEntityMember) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        customentity_member_in_db: md.CustomEntityMember = session.query(md.CustomEntityMember).filter_by(id=customentity_member_model.id).first()
        if customentity_member_in_db:
            return True
        return False

    def update(self, customentity_member_model: md.CustomEntityMember) -> None:
        """Updates custom entity member"""
        customentity_member_in_db: md.CustomEntityMember = session.query(md.CustomEntityMember).filter_by(id=customentity_member_model.id).first()
        customentity_member_in_db.name = customentity_member_model.name
        customentity_member_in_db.code = customentity_member_model.code
        customentity_member_in_db.group_id = customentity_member_model.group_id

        try:
            assert str(customentity_member_in_db.custom_entity_id) == str(customentity_member_model.custom_entity_id)
        except AssertionError:
            print("something's fucked up")
        
        session.commit()

    def create(self, customentity_member_model: md.CustomEntityMember) -> None:
        """Creates custom entity member"""
        session.add(customentity_member_model)
        session.commit()