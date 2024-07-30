from datetime import datetime, timedelta
import typing as tp

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import Engine

import aftafa.client.mvideo.models as md
from aftafa.client.mvideo.models import session, engine
import aftafa.client.mvideo.schemas as sc
from aftafa.utils.helpers import bcolors


class ProductDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    def check_for_group(self, schema_: sc.GetCatalogResponseContentElement) -> None:
        group_in_db: md.Group = session.query(md.Group).filter(md.Group.id == schema_.group_id).first()
        if not group_in_db:
            session.add(
                md.Group(
                    id=schema_.group_id,
                    name=schema_.group_name
                )
            )
            session.commit()
            return None
        try:
            assert group_in_db.name == schema_.group_name, f"group names are different in DB for group id {schema_.group_id}"
        except AssertionError as err:
            print(err)

    def check_for_brand(self, schema_: sc.GetCatalogResponseContentElement) -> None:
        if not schema_.brand_id:
            return False
        brand_in_db: md.Brand = session.query(md.Brand).filter(md.Brand.id == schema_.brand_id).first()
        if not brand_in_db:
            session.add(
                md.Brand(
                    id=schema_.brand_id,
                    name=schema_.brand_name
                )
            )
            session.commit()
            return None
        try:
            assert brand_in_db.name == schema_.brand_name, f"brand names are different in DB for brand id {schema_.brand_id}"
        except AssertionError as err:
            print(err)
    
    def prep_model(self, schema_: sc.GetCatalogResponseContentElement) -> md.Product:
        """prepares ORM model for a given schema"""
        # def convert_types(prod_schema_: dict[str, tp.Any]) -> dict[str, tp.Any]:
        #     prod_schema_['brand_id'] = int(prod_schema_['brand_id'])
        #     prod_schema_['group_id'] = int(prod_schema_['group_id'])
        #     prod_schema_['material_number'] = int(prod_schema_['material_number'])
        #     prod_schema_['sap_code_eldorado'] = int(prod_schema_['sap_code_eldorado'])
        #     return prod_schema_
            
        req_fields: list[str] = [i for i in md.Product.__dict__ if not i.startswith('_')]
        prod_schema: dict[str, tp.Any] = schema_.dict(by_alias=False)
        self.check_for_group(schema_=schema_)
        self.check_for_brand(schema_=schema_)

        prod_schema = {key: value for key, value in prod_schema.items() if key in req_fields}
        return md.Product(**prod_schema)

    def check_integrity(self, product_model: md.Product) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: md.Product = session.query(md.Product).filter(md.Product.material_number == int(product_model.material_number)).first()
        if prod_in_db:
            return True
        return False

    def update(self, product_model: md.Product) -> None:
        """Updates Product entity"""
        product_in_db: md.Product = session.query(md.Product).filter(md.Product.material_number == product_model.material_number).first()
        product_in_db.name = product_model.name
        product_in_db.material_model_name = product_model.material_model_name,
        product_in_db.material_account_name = product_model.material_account_name
        product_in_db.supplier_material_number = product_model.supplier_material_number
        product_in_db.retail_network_mvideo = product_model.retail_network_mvideo
        product_in_db.retail_network_eldorado = product_model.retail_network_eldorado

        product_in_db.product_type = product_model.product_type
        product_in_db.life_cycle_status = product_model.life_cycle_status        
        product_in_db.manufacturer_code = product_model.manufacturer_code
        product_in_db.main_image = product_model.main_image
        product_in_db.unit = product_model.unit
        product_in_db.review_status = product_model.review_status
        product_in_db.archived = product_model.archived

        # product_in_db.created_date = product_model.created_date           # FIXME: Implement Slowly changing dimension
        # product_in_db.group_id = product_model.group_id

        session.commit()

        try:
            assert int(product_in_db.group_id) == int(product_model.group_id), f"for this product {product_in_db.material_number} not the same groups"
            # assert int(product_in_db.sap_code_eldorado) == int(product_model.sap_code_eldorado), f"for this product {product_in_db.material_number} not the same eldorado code"
            # assert product_in_db.created_date == datetime.strptime(product_model.created_date, '%Y-%m-%dT%H:%M:%S.%fZ'), f"for this product {product_in_db.material_number} not the same created date"
        except AssertionError as err:
            print(err)
        

    def create(self, product_model: md.Product) -> None:
        """Creates Product entity"""
        session.add(product_model)
        session.commit()


class ProductPriceDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine

    # def check_for_brand(self, schema_: sc.GetCatalogResponseContentElement) -> None:
    #     brand_in_db: md.Brand = session.query(md.Brand).filter(md.Brand.id == schema_.brand_id).first()
    #     if not brand_in_db:
    #         session.add(
    #             md.Brand(
    #                 id=schema_.brand_id,
    #                 name=schema_.brand_name
    #             )
    #         )
    #         session.commit()
    #         return None
    #     try:
    #         assert brand_in_db.name == schema_.brand_name, f"brand names are different in DB for brand id {schema_.brand_id}"
    #     except AssertionError as err:
    #         print(err)
    
    def prep_model(self, schema_: sc.GetCatalogResponseContentElementPricesPriceEntry) -> md.ProductPrice:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in md.ProductPrice.__dict__ if not i.startswith('_')]
        prod_schema: dict[str, tp.Any] = schema_.dict(by_alias=False)
        prod_schema['price_uuid'] = prod_schema['uid']
        prod_schema['material_number'] = prod_schema['material_code']
        if not prod_schema['market_price_status']:                                  # FIXME: not supposed to be this way!
            prod_schema['market_price_status'] = 'NORMAL'

        prod_schema = {key: value for key, value in prod_schema.items() if key in req_fields}
        return md.ProductPrice(**prod_schema)

    def check_integrity(self, product_model: md.ProductPrice) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: md.ProductPrice = session.query(md.ProductPrice).filter(
            md.ProductPrice.material_number == int(product_model.material_number),
            md.ProductPrice.price_uuid == product_model.price_uuid
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, product_model: md.ProductPrice) -> None:
        """Updates Product entity"""
        product_in_db: md.ProductPrice = session.query(md.ProductPrice).filter(
            md.ProductPrice.material_number == int(product_model.material_number),
            md.ProductPrice.price_uuid == product_model.price_uuid

        ).first()

        product_in_db.price_type = product_model.price_type
        # product_in_db.price = product_model.price
        # product_in_db.promo_price = product_model.promo_price
        product_in_db.market_price = product_model.market_price
        product_in_db.currency = product_model.currency
        product_in_db.date_start = product_model.date_start
        product_in_db.date_end = product_model.date_end
        
        product_in_db.export_status = product_model.export_status
        product_in_db.approval_status = product_model.approval_status
        product_in_db.market_price_status = product_model.market_price_status

        session.commit()

        try:
            assert int(product_in_db.price) == int(product_model.price), f"for this product {product_in_db.material_number} not the same prices"
            assert product_in_db.promo_price == product_model.promo_price, f"for this product {product_in_db.material_number} not the same promo prices"
        except AssertionError as err:
            print(err)
        

    def create(self, product_model: md.ProductPrice) -> None:
        """Creates Product entity"""
        session.add(product_model)
        session.commit()


class OrderDBWriter:
    def __init__(self, supplier_code: str, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.supplier_code = supplier_code
        self.random_ts = datetime.now()
    
    def prep_model(self, schema_: sc.GetOrdersResponseContentElement) -> md.Order:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in md.Order.__dict__ if not i.startswith('_')]
        order_schema: dict[str, tp.Any] = schema_.dict(by_alias=False)
        order_schema['order_uuid'] = order_schema['uid']
        order_schema['order_number'] = order_schema['number']
        # order_schema['supplier_code'] = self.supplier_code

        order_schema = {key: value for key, value in order_schema.items() if key in req_fields}
        return md.Order(**order_schema)

    def check_integrity(self, order_model: md.Order) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_in_db: md.Order = session.query(md.Order).filter(
            md.Order.supplier_code == order_model.supplier_code,
            md.Order.order_number == order_model.order_number,
            md.Order.order_uuid == order_model.order_uuid
        ).first()
        if order_in_db:
            return True
        return False

    def update(self, order_model: md.Order) -> None:
        """Updates Product entity"""
        order_in_db: md.Order = session.query(md.Order).filter(
            md.Order.supplier_code == order_model.supplier_code,
            md.Order.order_number == order_model.order_number,
            md.Order.order_uuid == order_model.order_uuid
        ).first()

        order_in_db.status = order_model.status
        order_in_db.type_of_sale = order_model.type_of_sale

        session.commit()

        # try:
        #     assert int(order_in_db.price) == int(order_model.price), f"for this product {order_in_db.material_number} not the same prices"
        #     assert order_in_db.promo_price == order_model.promo_price, f"for this product {order_in_db.material_number} not the same promo prices"
        # except AssertionError as err:
        #     print(err)
        

    def create(self, order_model: md.Order) -> None:
        """Creates Order entity"""
        session.add(order_model)
        session.commit()


class OrderEntryDBWriter:
    def __init__(self, order_number: str, db_session: Session = session, db_engine: Engine = engine, extraction_ts: datetime | None = None) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.order_number = order_number
        if not extraction_ts:
            self.random_ts = datetime.now()
        else:
            self.random_ts = extraction_ts
    
    def prep_model(self, schema_: sc.GetOrderEntriesResponseContentElement) -> md.OrderEntry:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in md.OrderEntry.__dict__ if not i.startswith('_')]
        order_entry_schema: dict[str, tp.Any] = schema_.dict(by_alias=False)
        order_entry_schema['order_entry_uuid'] = order_entry_schema['uid']
        order_entry_schema['order_number'] = self.order_number
        order_entry_schema['extracted_at'] = self.random_ts
        order_entry_schema['updated_at'] = self.random_ts

        order_entry_schema = {key: value for key, value in order_entry_schema.items() if key in req_fields}
        return md.OrderEntry(**order_entry_schema)

    def check_integrity(self, order_entry_model: md.OrderEntry) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_entry_queried: md.OrderEntry = session.query(md.OrderEntry).filter(
            md.OrderEntry.order_number == order_entry_model.order_number,
            md.OrderEntry.material_supplier_code == order_entry_model.material_supplier_code
        )
        if order_entry_queried.count() > 1:
            print(f"This order entry {order_entry_model.order_entry_uuid} has duplicates")
        order_entry_in_db = order_entry_queried.first()
        if order_entry_in_db:
            return True
        return False

    def update(self, order_entry_model: md.OrderEntry) -> None:
        """Updates Product entity"""
        order_entry_in_db: md.OrderEntry = session.query(md.OrderEntry).filter(
            md.OrderEntry.order_number == order_entry_model.order_number,
            md.OrderEntry.material_supplier_code == order_entry_model.material_supplier_code
        ).first()

        not_updated_cols = [
            'id',
            'order_entry_uuid',
            'order_number',
            'material_supplier_code',
            'extracted_at'
        ]

        for attr_pair in [(k, v) for k, v in order_entry_model.__dict__.items() if not k.startswith('_') and not k in not_updated_cols]:
                order_entry_in_db.__setattr__(attr_pair[0], attr_pair[1])

        session.commit()

        try:
            assert int(order_entry_in_db.material_supplier_code) == int(order_entry_model.material_supplier_code), f"for this order_entry {order_entry_in_db.order_entry_uuid} not the same material codes"
        except AssertionError as err:
            print(err)
        

    def create(self, order_entry_model: md.OrderEntry) -> None:
        """Creates Order entity"""
        session.add(order_entry_model)
        session.commit()


class ProductMovementDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.random_ts = datetime.now()
    
    def prep_model(self, schema_: sc.GetProductMovementsResponseContentElement) -> md.ProductMovement:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in md.ProductMovement.__dict__ if not i.startswith('_')]
        product_movement_schema: dict[str, tp.Any] = schema_.dict(by_alias=False)
        product_movement_schema['product_movement_uuid'] = product_movement_schema['uid']
        product_movement_schema['material_number'] = product_movement_schema['zmaterial']
        product_movement_schema['object_number'] = product_movement_schema['zplant']
        product_movement_schema['quantity'] = product_movement_schema['qty']
        product_movement_schema['extracted_at'] = self.random_ts
        product_movement_schema['updated_at'] = self.random_ts

        product_movement_schema = {key: value for key, value in product_movement_schema.items() if key in req_fields}
        return md.ProductMovement(**product_movement_schema)

    def check_integrity(self, product_movement_model: md.ProductMovement) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        product_movement_queried: md.ProductMovement = session.query(md.ProductMovement).filter(
            md.ProductMovement.material_number == product_movement_model.material_number,
            md.ProductMovement.product_movement_uuid == product_movement_model.product_movement_uuid
        )
        if product_movement_queried.count() > 1:
            print(f"This order entry {product_movement_model.product_movement_uuid} has duplicates")
        product_movement_in_db = product_movement_queried.first()
        if product_movement_in_db:
            return True
        return False

    def update(self, product_movement_model: md.ProductMovement) -> None:
        """Updates Product entity"""
        product_movement_in_db: md.ProductMovement = session.query(md.ProductMovement).filter(
            md.ProductMovement.material_number == product_movement_model.material_number,
            md.ProductMovement.product_movement_uuid == product_movement_model.product_movement_uuid
        ).first()

        not_updated_cols = ['id', 'product_movement_uuid','material_number','extracted_at']

        for attr_pair in [(k, v) for k, v in product_movement_model.__dict__.items() if not k.startswith('_') and not k in not_updated_cols]:
                product_movement_in_db.__setattr__(attr_pair[0], attr_pair[1])
        # product_movement_in_db.quantity = product_movement_model.quantity

        session.commit()

        try:
            assert int(product_movement_in_db.material_number) == int(product_movement_model.material_number), f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same material codes"
            assert product_movement_in_db.state == product_movement_model.state, f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same states -> {product_movement_in_db.state} - {product_movement_model.state}"
            assert product_movement_in_db.status == product_movement_model.status, f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same statuss -> {product_movement_in_db.status} - {product_movement_model.status}"
            assert product_movement_in_db.object_number == product_movement_model.object_number, f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same object_numbers -> {product_movement_in_db.object_number} - {product_movement_model.object_number}"
            assert product_movement_in_db.object_type == product_movement_model.object_type, f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same object_types -> {product_movement_in_db.object_type} - {product_movement_model.object_type}"
            assert product_movement_in_db.quantity == int(product_movement_model.quantity), f"for this product_movement {product_movement_in_db.product_movement_uuid} not the same quantitys -> {product_movement_in_db.quantity} - {product_movement_model.quantity}"
        except AssertionError as err:
            print(err)
        

    def create(self, product_movement_model: md.ProductMovement) -> None:
        """Creates Order entity"""
        session.add(product_movement_model)
        session.commit()


class MailListDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
    
    def prep_model(self, dict_: dict) -> md.MailListSales:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [i for i in md.MailListSales.__dict__ if not i.startswith('_')]
        maillist_schema = {key: value for key, value in dict_.items() if key in req_fields}
        for key_ in (
                'business_unit',
                'category',
                'plan_name',
                'group',
                'sale_technology'
            ):
            if isinstance(maillist_schema[key_], float):
                maillist_schema[key_] = None

        model_to_add: md.MailListSales = md.MailListSales(**maillist_schema)
        return model_to_add

    def check_integrity(self, maillist_model: md.MailListSales) -> bool:
        material_number_queried: md.Product | None = session.query(md.Product).filter(
            md.Product.material_number == int(maillist_model.material_number)
        ).first()
        if not material_number_queried:
            print(f"There is no material number like this -> {str(maillist_model.material_number)}")
            return False
        return True

    def create(self, maillist_model: md.MailListSales) -> None:
        """Creates Product entity"""
        if self.check_integrity(maillist_model=maillist_model):
            session.add(maillist_model)
            session.commit()
            return None
        return None


class MailListStocksDBWriter:
    def __init__(self, db_session: Session = session, db_engine: Engine = engine) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
    
    def prep_model(self, dict_: dict) -> md.MailListStocks:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [i for i in md.MailListStocks.__dict__ if not i.startswith('_')]
        maillist_schema = {key: value for key, value in dict_.items() if key in req_fields}
        for key_ in (
                'object_number',
                'city',
                'object_type',
                'object_division',
                'storage_type',
                'product_type',
                'material_brand',
                'material_name'
            ):
            if isinstance(maillist_schema[key_], float):
                maillist_schema[key_] = None

        model_to_add: md.MailListStocks = md.MailListStocks(**maillist_schema)
        return model_to_add
    
    def check_integrity(self, maillist_model: md.MailListStocks) -> bool:
        material_number_queried: md.Product | None = session.query(md.Product).filter(
            md.Product.material_number == int(maillist_model.material_number)
        ).first()
        if not material_number_queried:
            print(f"There is no material number like this -> {str(maillist_model.material_number)}")
            return False
        return True

    def create(self, maillist_model: md.MailListStocks) -> None:
        """Creates Product entity"""
        if self.check_integrity(maillist_model=maillist_model):
            session.add(maillist_model)
            session.commit()
            return None
        return None
    