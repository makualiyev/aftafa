from datetime import datetime
from typing import Optional, Any

from sqlalchemy.exc import IntegrityError

import aftafa.client.yandex_market.models as ya_models
from aftafa.client.yandex_market.models import engine, session as db_session
import aftafa.client.yandex_market.schemas as ya_schemas
from aftafa.client.yandex_market.client import ClientSession
from aftafa.client.yandex_market.crud_base import order as order_crud
from aftafa.utils.helpers import flatten_dict


class DBShopSkuUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    def add_category(self, category_id_: int, category_name_: str) -> None:
        """
        checks whether category is presented in DB, and if not adds one
        """
        category_in_db: Optional[ya_models.Category] = db_session.query(ya_models.Category).filter(
                                                ya_models.Category.id == category_id_
                                            ).first()
        if category_in_db:
            try:
                assert category_in_db.name == category_name_, f'Category name is not the same in the DB, check it -> {category_id_} ({category_in_db.name})({category_name_})'
            except AssertionError as e:
                print(e)
            return None
        
        category_model: ya_models.Category = ya_models.Category(
            id=category_id_,
            name=category_name_
        )
        try:
            db_session.add(category_model)
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)

    def add_warehouse(self, warehouse_id: int, warehouse_name: str, shop_sku_: str) -> None:
        """
        checks whether warehouse is presented in DB, and if not adds one
        """
        warehouse_in_db: Optional[ya_models.Warehouse] = db_session.query(ya_models.Warehouse).filter(
                                                ya_models.Warehouse.id == warehouse_id
                                            ).first()
        if warehouse_in_db:
            try:
                assert warehouse_in_db.name == warehouse_name, f'warehouse name is not the same in the DB, check it -> {warehouse_id} [({warehouse_in_db.name}, {warehouse_name})]for this shopsku {shop_sku_}'
            except AssertionError as e:
                print(e)
            return None
        warehouse_model: ya_models.Warehouse = ya_models.Warehouse(
            id=warehouse_id,
            name=warehouse_name
        )
        try:
            db_session.add(warehouse_model)
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)

    def add_tariff(self, shop_sku_id_: int, tariff_cont: dict) -> None:
        """
        adds tariffs
        """
        tariff_in_db: ya_models.ShopSkuTariff = db_session.query(ya_models.ShopSkuTariff).filter(
            ya_models.ShopSkuTariff.shop_sku_id == shop_sku_id_,
            ya_models.ShopSkuTariff.tariff_type == tariff_cont['type']
        ).first()
        if tariff_in_db:
            tariff_in_db.amount = tariff_cont.get('amount')
            tariff_in_db.percent = tariff_cont.get('percent')
            db_session.commit()
            return True
        tariff_model: ya_models.ShopSkuTariff = ya_models.ShopSkuTariff(
            shop_sku_id=shop_sku_id_,
            tariff_type=tariff_cont['type'],
            amount = tariff_cont.get('amount'),
            percent = tariff_cont.get('percent')
        )
        try:
            db_session.add(tariff_model)
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)



    def process_shop_sku(self, shop_sku: dict) -> None:
        """
        processes shop_sku, but after it has done with shop skus
        """
        def check_in_db(shop_sku_code: str) -> bool | ya_models.ShopSku:
            """
            checks whether shop sku is in DB or not
            """
            shopsku_in_db: Optional[ya_models.ShopSku] = db_session.query(ya_models.ShopSku).filter(
                                                ya_models.ShopSku.shop_sku == shop_sku_code,
                                                ya_models.ShopSku.supplier_id == int(self.sesh.supplier.id)
                                            ).first()
            if not shopsku_in_db:
                return False
            return shopsku_in_db

        if shopsku_in_db := check_in_db(shop_sku_code=shop_sku['shopSku']):
            # update_shopsku
            shopsku_in_db.name = shop_sku['name']
            shopsku_in_db.price = (shop_sku.get('price'))
            if shop_sku.get('marketSku'):
                shopsku_in_db.market_sku = (shop_sku['marketSku'] if str(shop_sku['marketSku']) != '-1' and str(shop_sku['marketSku']) != '0' else None)

            shopsku_in_db.length = (shop_sku['weightDimensions'].get('length', 0.0))
            shopsku_in_db.width = (shop_sku['weightDimensions'].get('width', 0.0))
            shopsku_in_db.height = (shop_sku['weightDimensions'].get('height', 0.0))
            shopsku_in_db.weight = (shop_sku['weightDimensions'].get('weight', 0.0))
            
            db_session.commit()

            for tariff_cont in shop_sku['tariffs']:
                self.add_tariff(shop_sku_id_=shopsku_in_db.id, tariff_cont=tariff_cont)

            try:
                assert shopsku_in_db.category_id == shop_sku['categoryId'], f"categories are not the same for this shop sku -> {shop_sku['shopSku']}"
                assert float(shopsku_in_db.length) == (shop_sku['weightDimensions'].get('length', 0.0)), f"length are not the same for this shop sku -> {shop_sku['shopSku']}. check \
                {float(shopsku_in_db.length)} != {(shop_sku['weightDimensions'].get('length', 0.0))}"
                assert float(shopsku_in_db.width) == (shop_sku['weightDimensions'].get('width', 0.0)), f"width are not the same for this shop sku -> {shop_sku['shopSku']}. check \
                {float(shopsku_in_db.width)} != {(shop_sku['weightDimensions'].get('width', 0.0))}"
                assert float(shopsku_in_db.height) == (shop_sku['weightDimensions'].get('height', 0.0)), f"height are not the same for this shop sku -> {shop_sku['shopSku']}. check \
                {float(shopsku_in_db.height)} != {(shop_sku['weightDimensions'].get('height', 0.0))}"
                assert float(shopsku_in_db.weight) == (shop_sku['weightDimensions'].get('weight', 0.0)), f"weight are not the same for this shop sku -> {shop_sku['shopSku']}. check \
                {float(shopsku_in_db.weight)} != {(shop_sku['weightDimensions'].get('weight', 0.0))}"
            except AssertionError as e:
                print('Assertion error', e)
            return False

        # adding necessary info
        self.add_category(category_id_=shop_sku['categoryId'], category_name_=shop_sku['categoryName'])
        # if shop_sku.get('warehouses'):
        #     for wh in shop_sku.get('warehouses'):
        #         self.add_warehouse(warehouse_id=wh['id'], warehouse_name=wh['name'])
        
        shopsku_model: ya_models.ShopSku = ya_models.ShopSku(
            supplier_id=int(self.sesh.supplier.id),
            category_id=shop_sku['categoryId'],
            shop_sku=shop_sku['shopSku'],
            market_sku=(shop_sku.get('marketSku') if str(shop_sku.get('marketSku')) != '-1' or str(shop_sku.get('marketSku')) != '0' else None),
            name=shop_sku['name'],
            length=(shop_sku['weightDimensions'].get('length', 0.0)),
            width=(shop_sku['weightDimensions'].get('width', 0.0)),
            height=(shop_sku['weightDimensions'].get('height', 0.0)),
            weight=(shop_sku['weightDimensions'].get('weight', 0.0)),
            price=(shop_sku.get('price'))
        )
        try:
            db_session.add(shopsku_model)
            db_session.commit()

            shopsku_id_ = check_in_db(shop_sku_code=shop_sku['shopSku']).id
            for tariff_cont in shop_sku['tariffs']:
                self.add_tariff(shop_sku_id_=shopsku_id_, tariff_cont=tariff_cont)

        except IntegrityError as e:
            print(f"failed to commit ->", e)

    def process_shop_sku_stocks(self, shop_sku: dict) -> None:
        """
        processes shop_sku, but after it has done with shop skus
        """
        def check_stock_in_db(stock_entry: dict, shopsku_id_: int, wh_id_: int) -> None:
            stock_in_db: ya_models.ShopSkuStocks = db_session.query(ya_models.ShopSkuStocks).filter(
                ya_models.ShopSkuStocks.shop_sku_id == shopsku_id_,
                ya_models.ShopSkuStocks.stock_type == stock_entry['type'],
                ya_models.ShopSkuStocks.warehouse_id == wh_id_,
                ya_models.ShopSkuStocks.updated_at == datetime.now().date()
            ).first()
            if stock_in_db:
                stock_in_db.stock_count = stock_entry['count']
                db_session.commit()
                return True
            stock_model: ya_models.ShopSkuStocks = ya_models.ShopSkuStocks(
                shop_sku_id=shopsku_id_,
                warehouse_id=wh_id_,
                stock_type=stock_entry['type'],
                stock_count=stock_entry['count'],
                updated_at=datetime.now().date()
            )
            try:
                db_session.add(stock_model)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            
        
        shopsku_in_db: Optional[ya_models.ShopSku] = db_session.query(ya_models.ShopSku).filter(
                                            ya_models.ShopSku.shop_sku == shop_sku['shopSku'],
                                            ya_models.ShopSku.supplier_id == int(self.sesh.supplier.id)
                                        ).first()

        if not shop_sku.get('warehouses'):
            return None

        for wh in shop_sku.get('warehouses'):
            self.add_warehouse(warehouse_id=wh['id'], warehouse_name=wh['name'], shop_sku_=shop_sku['shopSku'])
            for stock_entry in wh['stocks']:
                check_stock_in_db(stock_entry=stock_entry, shopsku_id_=shopsku_in_db.id, wh_id_=wh['id'])


        


class DBOfferUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    ...
    # def __init__(
    #         self, client_session: ClientSession,
    #         db_session = db_session, db_engine = engine
    # ) -> None:
    #     self.db_session = db_session
    #     self.db_engine = db_engine
    #     self.sesh = client_session

    # def check_shop_sku(self, item_entry: str) -> int:
    #     shop_sku_in_db: ya_models.ShopSku = (
    #         db_session.query(ya_models.ShopSku)
    #                 .filter(
    #                     ya_models.ShopSku.supplier_id == int(self.sesh.supplier.id),
    #                     ya_models.ShopSku.shop_sku == item_entry['shopSku']
    #                 )
    #             )
    #     if shop_sku_in_db:
    #         return shop_sku_in_db.id
    #     print(f"Failed for this order item as it lacks shop sku in DB :( -> {item_entry['shopSku']} \t {self.sesh.supplier.name}")
    #     return -1

    # def prep_model(self, schema_: ya_schemas.OrdersStatsOrderDTO) -> ya_models.Order:
    #     """prepares ORM model for a given schema"""
    #     def find_shop_sku_id(schema_: dict) -> int:
    #         return int(db_session.query(ya_models.ShopSku).filter(
    #             ya_models.ShopSku.shop_sku == schema_['shop_sku'],
    #             ya_models.ShopSku.supplier_id == self.sesh.supplier.id
    #         ).first().id)
        
        
    #     req_fields: list[str] = [i for i in ya_models.Order.__dict__ if not i.startswith('_')]
    #     order_schema: dict[str, Any] = schema_.to_dict()
    #     order_main_schema = order_schema['main_order']
    #     order_main_schema['supplier_id'] = int(self.sesh.supplier.id)
    #     DBRegionUpdater(client_session=self.sesh).refresh(
    #                 region_schema_=order_main_schema['delivery_region']
    #             )

    #     order_main_schema = {key: value for key, value in order_main_schema.items() if key in req_fields}
        
    #     return ya_models.Order(**order_main_schema)
    
    # def check_integrity(self, order_model: ya_models.Order) -> bool:
    #     """
    #     Checks integrity, if True = create False = update
    #     """
    #     order_queried: ya_models.Order = self.db_session.query(ya_models.Order).filter(
    #         ya_models.Order.order_id == order_model.order_id,
    #         ya_models.Order.supplier_id == int(self.sesh.supplier.id)
    #     )
    #     if order_queried.count() > 1:
    #         print(f"This order entry {order_model.id} has duplicates")
    #     order_in_db = order_queried.first()
    #     if order_in_db:
    #         return True
    #     return False
    
    # def update(self, order_model: ya_models.Order) -> None:
    #     """Updates Product entity"""
    #     order_in_db: ya_models.Order = self.db_session.query(ya_models.Order).filter(
    #         ya_models.Order.order_id == order_model.order_id,
    #         ya_models.Order.supplier_id == int(self.sesh.supplier.id)
    #     ).first()

    #     order_in_db.partner_order_id = order_model.partner_order_id
    #     order_in_db.status = order_model.status
    #     order_in_db.status_update_date = order_model.status_update_date
    #     order_in_db.payment_type = order_model.payment_type


    #     self.db_session.commit()

    # def create(self, order_model: ya_models.Order) -> None:
    #     """Creates Order entity"""
    #     self.db_session.add(order_model)
    #     self.db_session.commit()

    # def populate_order(self, schema_: ya_schemas.OrdersStatsOrderDTO) -> ya_models.Order:
    #     order_schema: dict[str, Any] = schema_.to_dict()
        
    #     if order_schema.get('commissions')[0]:
    #         for commission_entry in order_schema.get('commissions')[1]:
    #             DBOrderCommissionsUpdater(client_session=self.sesh).refresh(
    #                 order_commission_schema=commission_entry
    #             )
    #     if order_schema.get('payments')[0]:
    #         for payment_entry in order_schema.get('payments')[1]:
    #             DBOrderPaymentsUpdater(client_session=self.sesh).refresh(
    #                 order_payment_schema=payment_entry
    #             )
    #     if order_schema.get('items')[0]:
    #         for order_item_entry in order_schema.get('items')[1]:
    #             DBOrderItemsUpdater(client_session=self.sesh).refresh(
    #                 order_item_schema=order_item_entry
    #             )
    #     if order_schema.get('initial_items')[0]:
    #         for order_item_entry in order_schema.get('initial_items')[1]:
    #             DBOrderItemsUpdater(client_session=self.sesh).refresh(
    #                 order_item_schema=order_item_entry
    #             )


    # def refresh(self, order_schema_: dict) -> None:
    #     order_model_ = self.prep_model(schema_=order_schema_)
    #     if self.check_integrity(order_model=order_model_):
    #         self.update(order_model=order_model_)
    #         return None
    #     self.create(order_model=order_model_)
    #     return None
    

class DBRegionUpdater:
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
    
    def prep_model(self, schema_: dict) -> ya_models.Region:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in ya_models.Region.__dict__ if not i.startswith('_')]
        region_schema = {key: value for key, value in schema_.items() if key in req_fields}
        return ya_models.Region(**region_schema)

    def check_integrity(self, region_model: ya_models.Region) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        region_queried: ya_models.Region = self.db_session.query(ya_models.Region).filter(
            ya_models.Region.id == region_model.id
        )
        if region_queried.count() > 1:
            print(f"This region entry {region_model.name} has duplicates")
        region_in_db = region_queried.first()
        if region_in_db:
            return True
        return False

    def update(self, region_model: ya_models.Region) -> None:
        """Updates Product entity"""
        region_in_db: ya_models.Region = self.db_session.query(ya_models.Region).filter(
            ya_models.Region.id == region_model.id
        ).first()

        region_in_db.name = region_model.name
        self.db_session.commit()        

    def create(self, region_model: ya_models.Region) -> None:
        """Creates Order entity"""
        self.db_session.add(region_model)
        self.db_session.commit()

    def refresh(self, region_schema_: dict) -> None:
        region_model_ = self.prep_model(schema_=region_schema_)
        if self.check_integrity(region_model=region_model_):
            self.update(region_model=region_model_)
            return None
        self.create(region_model=region_model_)
        return None
        

class DBWarehouseUpdater:
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
    
    def prep_model(self, schema_: dict) -> ya_models.Warehouse:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in ya_models.Warehouse.__dict__ if not i.startswith('_')]
        warehouse_schema = {key: value for key, value in schema_.items() if key in req_fields}
        return ya_models.Warehouse(**warehouse_schema)

    def check_integrity(self, warehouse_model: ya_models.Warehouse) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        warehouse_queried: ya_models.Warehouse = self.db_session.query(ya_models.Warehouse).filter(
            ya_models.Warehouse.id == warehouse_model.id
        )
        if warehouse_queried.count() > 1:
            print(f"This warehouse entry {warehouse_model.name} has duplicates")
        warehouse_in_db = warehouse_queried.first()
        if warehouse_in_db:
            return True
        return False

    def update(self, warehouse_model: ya_models.Warehouse) -> None:
        """Updates Product entity"""
        warehouse_in_db: ya_models.Warehouse = self.db_session.query(ya_models.Warehouse).filter(
            ya_models.Warehouse.id == warehouse_model.id
        ).first()

        warehouse_in_db.name = warehouse_model.name
        self.db_session.commit()

    def create(self, warehouse_model: ya_models.Warehouse) -> None:
        """Creates Order entity"""
        self.db_session.add(warehouse_model)
        self.db_session.commit()

    def refresh(self, warehouse_schema_: dict) -> None:
        warehouse_model_ = self.prep_model(schema_=warehouse_schema_)
        if self.check_integrity(warehouse_model=warehouse_model_):
            self.update(warehouse_model=warehouse_model_)
            return None
        self.create(warehouse_model=warehouse_model_)
        return None

class DBOrderCommissionsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_order_id(self, schema_: dict) -> int:
        """gets order_id"""
        order_queried = self.db_session.query(ya_models.Order).filter(
            ya_models.Order.order_id == schema_['order_id'],
            ya_models.Order.supplier_id == int(self.sesh.supplier.id)
        )
        if order_queried.count() > 1:
            print(f"This order {schema_['order_id']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        order_in_db = order_queried.first()
        if order_in_db:
            return order_in_db.id

    def prep_model(self, schema_: dict) -> ya_models.OrderCommissions:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in ya_models.OrderCommissions.__dict__ if not i.startswith('_')]
        # order_schema: dict[str, Any] = schema_.to_dict()

        order_commissions_schema = schema_
        order_commissions_schema['order_id'] = self.get_order_id(schema_=schema_)
        order_commissions_schema = {key: value for key, value in order_commissions_schema.items() if key in req_fields}
        return ya_models.OrderCommissions(**order_commissions_schema)
    
    def check_integrity(self, order_commission_model: ya_models.OrderCommissions) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_commissions_queried: ya_models.OrderCommissions = self.db_session.query(ya_models.OrderCommissions).filter(
            ya_models.OrderCommissions.order_id == order_commission_model.order_id,
            ya_models.OrderCommissions.type == order_commission_model.type
        )
        if order_commissions_queried.count() > 1:
            print(f"This order commission {order_commission_model.order_id} has duplicates")
        order_commission_in_db = order_commissions_queried.first()
        if order_commission_in_db:
            return True
        return False
    
    def update(self, order_commission_model: ya_models.OrderCommissions) -> None:
        """Updates Product entity"""
        order_commission_in_db: ya_models.OrderCommissions = self.db_session.query(ya_models.OrderCommissions).filter(
            ya_models.OrderCommissions.order_id == order_commission_model.order_id,
            ya_models.OrderCommissions.type == order_commission_model.type
        ).first()

        order_commission_in_db.actual = order_commission_model.actual
        order_commission_in_db.predicted = order_commission_model.predicted

        self.db_session.commit()

    def create(self, order_commission_model: ya_models.OrderCommissions) -> None:
        """Creates Order entity"""
        self.db_session.add(order_commission_model)
        self.db_session.commit()

    def refresh(self, order_commission_schema: dict) -> None:
        order_commission_model_ = self.prep_model(schema_=order_commission_schema)
        if self.check_integrity(order_commission_model=order_commission_model_):
            self.update(order_commission_model=order_commission_model_)
            return None
        self.create(order_commission_model=order_commission_model_)
        return None


class DBOrderPaymentsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_order_id(self, schema_: dict) -> int:
        """gets order_id"""
        order_queried = self.db_session.query(ya_models.Order).filter(
            ya_models.Order.order_id == schema_['order_id'],
            ya_models.Order.supplier_id == int(self.sesh.supplier.id)
        )
        if order_queried.count() > 1:
            print(f"This order {schema_['order_id']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        order_in_db = order_queried.first()
        if order_in_db:
            return order_in_db.id

    def prep_model(self, schema_: dict) -> ya_models.OrderPayments:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in ya_models.OrderPayments.__dict__ if not i.startswith('_')]
        # order_schema: dict[str, Any] = schema_.to_dict()

        order_payments_schema = schema_
        order_payments_schema['order_id'] = self.get_order_id(schema_=schema_)
        order_payments_schema = {key: value for key, value in order_payments_schema.items() if key in req_fields}
        return ya_models.OrderPayments(**order_payments_schema)
    
    def check_integrity(self, order_payment_model: ya_models.OrderPayments) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_payments_in_db: ya_models.OrderPayments = self.db_session.query(ya_models.OrderPayments).filter(
            ya_models.OrderPayments.order_id == order_payment_model.order_id,
            ya_models.OrderPayments.payment_id == order_payment_model.payment_id
        )
        if order_payments_in_db.count() > 1:
            print(f"This order payment with id - {order_payment_model.payment_id} for order - {order_payment_model.order_id} has duplicates")
        order_payments_in_db = order_payments_in_db.first()
        if order_payments_in_db:
            return True
        return False
    
    def update(self, order_payment_model: ya_models.OrderPayments) -> None:
        """Updates Product entity"""
        order_payment_in_db: ya_models.OrderPayments = self.db_session.query(ya_models.OrderPayments).filter(
            ya_models.OrderPayments.order_id == order_payment_model.order_id,
            ya_models.OrderPayments.payment_id == order_payment_model.payment_id
        ).first()

        order_payment_in_db.date = order_payment_model.date
        order_payment_in_db.type = order_payment_model.type
        order_payment_in_db.source = order_payment_model.source
        order_payment_in_db.total= order_payment_model.total

        self.db_session.commit()

    def create(self, order_payment_model: ya_models.OrderPayments) -> None:
        """Creates Order entity"""
        self.db_session.add(order_payment_model)
        self.db_session.commit()

    def refresh(self, order_payment_schema: dict) -> None:
        order_payment_model_ = self.prep_model(schema_=order_payment_schema)
        if self.check_integrity(order_payment_model=order_payment_model_):
            self.update(order_payment_model=order_payment_model_)
            return None
        self.create(order_payment_model=order_payment_model_)
        return None
    

class DBOrderItemsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_order_id(self, schema_: dict) -> int:
        """gets order_id"""
        order_queried = self.db_session.query(ya_models.Order).filter(
            ya_models.Order.order_id == schema_['order_id'],
            ya_models.Order.supplier_id == int(self.sesh.supplier.id)
        )
        if order_queried.count() > 1:
            print(f"This order {schema_['order_id']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        order_in_db = order_queried.first()
        if order_in_db:
            return order_in_db.id
        
    def get_shop_sku_id(self, schema_: dict) -> int:
        """finds a shop sku id for a given shop sku"""
        shop_sku_id_queried = self.db_session.query(ya_models.ShopSku).filter(
            ya_models.ShopSku.shop_sku == str(schema_['shop_sku']),
            ya_models.ShopSku.supplier_id == int(self.sesh.supplier.id)
        )
        if shop_sku_id_queried.count() > 1:
            print(f"This shop sku {schema_['shop_sku']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        shop_sku_in_db = shop_sku_id_queried.first()
        if shop_sku_in_db:
            return shop_sku_in_db.id
        else:
            print(f"FATAL error -> this shop sku can't be found {schema_['shop_sku']}")

    def prep_model(self, schema_: dict) -> ya_models.OrderItem:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in ya_models.OrderItem.__dict__ if not i.startswith('_')]
        # order_schema: dict[str, Any] = schema_.to_dict()

        order_items_schema = schema_
        order_items_schema['order_id'] = self.get_order_id(schema_=schema_)
        order_items_schema['shop_sku_id'] = self.get_shop_sku_id(schema_=schema_)
        DBWarehouseUpdater(client_session=self.sesh).refresh(
                    warehouse_schema_=order_items_schema['warehouse']
                )
        
        order_items_schema = {key: value for key, value in order_items_schema.items() if key in req_fields}
        return ya_models.OrderItem(**order_items_schema)
    
    def check_integrity(self, order_item_model: ya_models.OrderItem) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_items_in_db: ya_models.OrderItem = self.db_session.query(ya_models.OrderItem).filter(
            ya_models.OrderItem.order_id == order_item_model.order_id,
            ya_models.OrderItem.shop_sku_id == order_item_model.shop_sku_id
        )
        if order_items_in_db.count() > 1:
            print(f"This order item with id - {order_item_model.shop_sku_id} for order - {order_item_model.order_id} has duplicates")
        order_items_in_db = order_items_in_db.first()
        if order_items_in_db:
            return True
        return False
    
    def update(self, order_item_model: ya_models.OrderItem) -> None:
        """Updates Product entity"""
        order_item_in_db: ya_models.OrderItem = self.db_session.query(ya_models.OrderItem).filter(
            ya_models.OrderItem.order_id == order_item_model.order_id,
            ya_models.OrderItem.shop_sku_id == order_item_model.shop_sku_id
        ).first()

        try:    
            assert order_item_in_db.offer_name == order_item_model.offer_name, f"This attribute {order_item_in_db.offer_name} doesn't match with those from API ({order_item_model.offer_name}) for this order ({order_item_model.order_id})"
            assert int(order_item_in_db.market_sku) == int(order_item_model.market_sku), f"This attribute {order_item_in_db.market_sku} doesn't match with those from API ({order_item_model.market_sku}) for this order ({order_item_model.order_id})"
            assert order_item_in_db.count == order_item_model.count, f"This attribute {order_item_in_db.count} doesn't match with those from API ({order_item_model.count}) for this order ({order_item_model.order_id})"
            assert order_item_in_db.warehouse_id== order_item_model.warehouse_id, f"This attribute {order_item_in_db.warehouse_id} doesn't match with those from API ({order_item_model.warehouse_id}) for this order ({order_item_model.order_id})"
        except AssertionError as e:
            print(e)

        self.db_session.commit()

    def create(self, order_item_model: ya_models.OrderItem) -> None:
        """Creates Order entity"""
        self.db_session.add(order_item_model)
        self.db_session.commit()

    def refresh(self, order_item_schema: dict) -> None:
        order_item_model_ = self.prep_model(schema_=order_item_schema)
        if self.check_integrity(order_item_model=order_item_model_):
            self.update(order_item_model=order_item_model_)
            self.populate_order_item(schema_=order_item_schema)
            return None
        self.create(order_item_model=order_item_model_)
        self.populate_order_item(schema_=order_item_schema)
        return None
    
    def populate_order_item(self, schema_: dict) -> None:
        # order_item_schema: dict[str, Any] = schema_.to_dict()
        order_item_schema: dict[str, Any] = schema_
        
        if order_item_schema['attrs'].get('prices')[0]:
            for order_item_price_entry in order_item_schema['attrs'].get('prices')[1]:
                order_item_price_entry['order_id'] = order_item_schema['order_id']
                order_item_price_entry['shop_sku'] = order_item_schema['shop_sku']
                order_crud.DBOrderItemsPriceUpdater(client_session=self.sesh, db_session=self.db_session, db_engine=self.db_engine).refresh(
                    order_item_price_schema=order_item_price_entry
                )

        # if order_item_schema['attrs'].get('details')[0]:
        #     detail_count: int = len(order_item_schema['attrs'].get('details')[1])
        #     if order_item_schema.get('count'):
        #         item_count: int = order_item_schema.get('count')
        #     else:
        #         item_count: int = order_item_schema.get('initial_count')

        #     for order_item_detail_entry in order_item_schema['attrs'].get('details')[1]:
        #         order_item_detail_entry['order_id'] = order_item_schema['order_id']
        #         order_item_detail_entry['shop_sku'] = order_item_schema['shop_sku']
        #         order_item_detail_entry['item_count'] = item_count
        #         order_crud.DBOrderItemsDetailsUpdater(client_session=self.sesh, db_session=self.db_session, db_engine=self.db_engine).refresh(
        #             order_item_details_schema=order_item_detail_entry
        #         )
    

class DBOrderUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def check_shop_sku(self, item_entry: str) -> int:
        shop_sku_in_db: ya_models.ShopSku = (
            db_session.query(ya_models.ShopSku)
                    .filter(
                        ya_models.ShopSku.supplier_id == int(self.sesh.supplier.id),
                        ya_models.ShopSku.shop_sku == item_entry['shopSku']
                    )
                )
        if shop_sku_in_db:
            return shop_sku_in_db.id
        print(f"Failed for this order item as it lacks shop sku in DB :( -> {item_entry['shopSku']} \t {self.sesh.supplier.name}")
        return -1

    def prep_model(self, schema_: ya_schemas.OrdersStatsOrderDTO) -> ya_models.Order:
        """prepares ORM model for a given schema"""
        def find_shop_sku_id(schema_: dict) -> int:
            return int(db_session.query(ya_models.ShopSku).filter(
                ya_models.ShopSku.shop_sku == schema_['shop_sku'],
                ya_models.ShopSku.supplier_id == self.sesh.supplier.id
            ).first().id)
        
        
        req_fields: list[str] = [i for i in ya_models.Order.__dict__ if not i.startswith('_')]
        order_schema: dict[str, Any] = schema_.to_dict()
        order_main_schema = order_schema['main_order']
        order_main_schema['supplier_id'] = int(self.sesh.supplier.id)
        DBRegionUpdater(client_session=self.sesh).refresh(
                    region_schema_=order_main_schema['delivery_region']
                )

        order_main_schema = {key: value for key, value in order_main_schema.items() if key in req_fields}
        
        return ya_models.Order(**order_main_schema)
    
    def check_integrity(self, order_model: ya_models.Order) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_queried: ya_models.Order = self.db_session.query(ya_models.Order).filter(
            ya_models.Order.order_id == order_model.order_id,
            ya_models.Order.supplier_id == int(self.sesh.supplier.id)
        )
        if order_queried.count() > 1:
            print(f"This order entry {order_model.id} has duplicates")
        order_in_db = order_queried.first()
        if order_in_db:
            return True
        return False
    
    def update(self, order_model: ya_models.Order) -> None:
        """Updates Product entity"""
        order_in_db: ya_models.Order = self.db_session.query(ya_models.Order).filter(
            ya_models.Order.order_id == order_model.order_id,
            ya_models.Order.supplier_id == int(self.sesh.supplier.id)
        ).first()

        order_in_db.partner_order_id = order_model.partner_order_id
        order_in_db.status = order_model.status
        order_in_db.status_update_date = order_model.status_update_date
        order_in_db.payment_type = order_model.payment_type


        self.db_session.commit()

    def create(self, order_model: ya_models.Order) -> None:
        """Creates Order entity"""
        self.db_session.add(order_model)
        self.db_session.commit()

    def populate_order(self, schema_: ya_schemas.OrdersStatsOrderDTO) -> ya_models.Order:
        order_schema: dict[str, Any] = schema_.to_dict()
        
        if order_schema.get('commissions')[0]:
            for commission_entry in order_schema.get('commissions')[1]:
                DBOrderCommissionsUpdater(client_session=self.sesh).refresh(
                    order_commission_schema=commission_entry
                )
        if order_schema.get('payments')[0]:
            for payment_entry in order_schema.get('payments')[1]:
                DBOrderPaymentsUpdater(client_session=self.sesh).refresh(
                    order_payment_schema=payment_entry
                )
        if order_schema.get('items')[0]:
            for order_item_entry in order_schema.get('items')[1]:
                DBOrderItemsUpdater(client_session=self.sesh).refresh(
                    order_item_schema=order_item_entry
                )
        if order_schema.get('initial_items')[0]:
            for order_item_entry in order_schema.get('initial_items')[1]:
                DBOrderItemsUpdater(client_session=self.sesh).refresh(
                    order_item_schema=order_item_entry
                )


    def refresh(self, order_schema_: dict) -> None:
        order_model_ = self.prep_model(schema_=order_schema_)
        if self.check_integrity(order_model=order_model_):
            self.update(order_model=order_model_)
            return None
        self.create(order_model=order_model_)
        return None
    


class DBOfferPriceUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session = db_session, db_engine = engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
    
    def prep_model(self, schema_: ya_schemas.OfferPriceResponseDTO) -> ya_models.OfferPrice:
        """prepares ORM model for a given schema"""
        def find_shop_sku_id(schema_: dict) -> int:
            return int(db_session.query(ya_models.ShopSku).filter(
                ya_models.ShopSku.shop_sku == schema_['shop_sku'],
                ya_models.ShopSku.supplier_id == self.sesh.supplier.id
            ).first().id)
            
        req_fields: list[str] = [i for i in ya_models.OfferPrice.__dict__ if not i.startswith('_')]
        offer_price_dto_schema: dict[str, Any] = flatten_dict(schema_.dict(by_alias=False))
        offer_price_dto_schema_ = {k: v for k, v in offer_price_dto_schema.items() if not k.startswith('price.')}
        offer_price_dto_schema_.update({k[6:]: v for k, v in offer_price_dto_schema.items() if k.startswith('price.')})
        offer_price_dto_schema_['shop_sku'] = offer_price_dto_schema_['id']
        offer_price_dto_schema_['shop_sku_id'] = find_shop_sku_id(schema_=offer_price_dto_schema_)
        offer_price_dto_schema_['supplier_id'] = int(self.sesh.supplier.id)

        offer_price_dto_schema_.pop('id')

        offer_price_dto_schema_ = {key: value for key, value in offer_price_dto_schema_.items() if key in req_fields}
        return ya_models.OfferPrice(**offer_price_dto_schema_)

    def check_integrity(self, offer_price_model: ya_models.OfferPrice) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        offer_price_queried: ya_models.OfferPrice = db_session.query(ya_models.OfferPrice).filter(
            ya_models.OfferPrice.shop_sku_id == offer_price_model.shop_sku_id,
            ya_models.OfferPrice.fetched_at == datetime.now().date()
        )
        if offer_price_queried.count() > 1:
            print(f"This offer price entry {offer_price_model.shop_sku} has duplicates")
        offer_price_in_db = offer_price_queried.first()
        if offer_price_in_db:
            return True
        return False

    def update(self, offer_price_model: ya_models.OfferPrice) -> None:
        """Updates Product entity"""
        offer_price_in_db: ya_models.OfferPrice = db_session.query(ya_models.OfferPrice).filter(
            ya_models.OfferPrice.shop_sku_id == offer_price_model.shop_sku_id,
            ya_models.OfferPrice.fetched_at == datetime.now().date()
        ).first()

        offer_price_in_db.value = offer_price_model.value
        offer_price_in_db.discount_base = offer_price_model.discount_base
        offer_price_in_db.updated_at = offer_price_model.updated_at

        db_session.commit()
        # try:
        #     assert int(offer_price_in_db.material_number) == int(offer_price_model.material_number), f"for this product_movement {offer_price_in_db.product_movement_uuid} not the same material codes"
        # except AssertionError as err:
        #     print(err)
        

    def create(self, offer_price_model: ya_models.OfferPrice) -> None:
        """Creates Order entity"""
        db_session.add(offer_price_model)
        db_session.commit()



class DBWebCatalogUpdater:
    """
    """
    def __init__(self, extraction_ts: datetime) -> None:
        self.db_session = db_session
        self.extraction_ts = extraction_ts

    def prep_model(self, schema_: dict) -> ya_models.WebCatalogProduct:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in ya_models.WebCatalogProduct.__dict__ if not i.startswith('_')]
        web_catalog_schema: dict[str, str] = schema_
        web_catalog_schema['extracted_at'] = self.extraction_ts
        web_catalog_schema = {key: value for key, value in web_catalog_schema.items() if key in req_fields}
        return ya_models.WebCatalogProduct(**web_catalog_schema)

    def check_integrity(self, web_catalog_product_model: ya_models.WebCatalogProduct) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        web_catalog_in_db: ya_models.WebCatalogProduct = self.db_session.query(ya_models.WebCatalogProduct).filter(
            ya_models.WebCatalogProduct.meta_supplier == str(web_catalog_product_model.meta_supplier),
            ya_models.WebCatalogProduct.offer_id == web_catalog_product_model.offer_id,
            ya_models.WebCatalogProduct.meta_report_date == web_catalog_product_model.meta_report_date
        ).first()
        if web_catalog_in_db:
            return True
        return False

    def update(self, web_catalog_product_model: ya_models.WebCatalogProduct) -> None:
        """Updates Product entity"""
        web_catalog_product_model: ya_models.WebCatalogProduct = self.db_session.query(ya_models.WebCatalogProduct).filter(
            ya_models.WebCatalogProduct.meta_supplier == str(web_catalog_product_model.meta_supplier),
            ya_models.WebCatalogProduct.offer_id == web_catalog_product_model.offer_id,
            ya_models.WebCatalogProduct.meta_report_date == web_catalog_product_model.meta_report_date
        ).first()

        web_catalog_product_model.available_count = web_catalog_product_model.available_count
        self.db_session.commit()
        return web_catalog_product_model.id

    def create(self, web_catalog_product_model: ya_models.WebCatalogProduct) -> int:
        """Creates Product entity"""
        self.db_session.add(web_catalog_product_model)
        self.db_session.commit()
        return web_catalog_product_model.id
      
    # def populate_web_catalog_product(self, schema_: dict[str, str], web_catalog_product_id_in_db: int) -> None:
    #     if schema_.get("sizes"):
    #         for size_ in schema_.get('sizes'):
    #             size_['price_basic'] = size_.get('price')['basic']
    #             size_['price_product'] = size_.get('price')['product']
    #             size_['price_total'] = size_.get('price')['total']
    #             size_['price_logistics'] = size_.get('price')['logistics']
    #             size_['price_return_'] = size_.get('price')['return_']

    #             DBWebCatalogProductSizeUpdater(extraction_ts=self.extraction_ts).refresh(
    #                 web_catalog_product_size_schema_=size_,
    #                 web_catalog_product_id_in_db=web_catalog_product_id_in_db
    #             )

    def refresh(self, web_catalog_product_schema_: dict) -> None:
        web_catalog_product_model = self.prep_model(schema_=web_catalog_product_schema_)
        if self.check_integrity(web_catalog_product_model=web_catalog_product_model):
            web_catalog_product_id: int = self.update(web_catalog_product_model=web_catalog_product_model)
            # self.populate_web_catalog_product(schema_=web_catalog_product_schema_, web_catalog_product_id_in_db=web_catalog_product_id)
            return None
        web_catalog_product_id: int = self.create(web_catalog_product_model=web_catalog_product_model)
        # self.populate_web_catalog_product(schema_=web_catalog_product_schema_, web_catalog_product_id_in_db=web_catalog_product_id)
        return None
