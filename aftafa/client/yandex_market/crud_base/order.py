from sqlalchemy.exc import IntegrityError

import aftafa.client.yandex_market.models as ya_models
from aftafa.client.yandex_market.client import ClientSession


class DBOrderItemsPriceUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session, db_engine
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
        if order_queried.count() == 0:
            print(f"This order {schema_['order_id']} for this supplier ( {self.sesh.supplier.id} ) doesn't have a represantiton in db")
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

    def get_order_item_id(self, schema_: dict) -> int:
        order_item_queried = self.db_session.query(ya_models.OrderItem).filter(
            ya_models.OrderItem.shop_sku_id == int(schema_['shop_sku_id']),
            ya_models.OrderItem.order_id == int(schema_['order_id'])
        )
        if order_item_queried.count() > 1:
            print(f"This order item with order id {schema_['order_id']}, {schema_['shop_sku']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        order_item_in_db = order_item_queried.first()
        if order_item_in_db:
            return order_item_in_db.id
        else:
            print(f"FATAL error -> this shop sku can't be found {schema_['shop_sku']}")

    def prep_model(self, schema_: dict) -> ya_models.OrderItemPrice:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in ya_models.OrderItemPrice.__dict__ if not i.startswith('_')]
        # order_schema: dict[str, Any] = schema_.to_dict()

        order_item_price_schema = schema_
        # order_item_price_schema['order_id'] = self.get_order_id(schema_=schema_)
        order_item_price_schema['shop_sku_id'] = self.get_shop_sku_id(schema_=schema_)
        order_item_price_schema['order_item_id'] = self.get_order_item_id(schema_=order_item_price_schema)
        order_item_price_schema['price_type'] = order_item_price_schema['type']
        
        order_item_price_schema = {key: value for key, value in order_item_price_schema.items() if key in req_fields}
        return ya_models.OrderItemPrice(**order_item_price_schema)
    
    def check_integrity(self, order_item_price_model: ya_models.OrderItemPrice) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_items_in_db: ya_models.OrderItemPrice = self.db_session.query(ya_models.OrderItemPrice).filter(
            ya_models.OrderItemPrice.order_item_id == order_item_price_model.order_item_id,
            ya_models.OrderItemPrice.price_type == order_item_price_model.price_type
        )
        if order_items_in_db.count() > 1:
            print(f"This order item with id - {order_item_price_model.order_item_id} for this price type ({order_item_price_model.price_type}) has duplicates")
        order_items_in_db = order_items_in_db.first()
        if order_items_in_db:
            return True
        return False
    
    def update(self, order_item_price_model: ya_models.OrderItemPrice) -> None:
        """Updates Product entity"""
        order_item_price_in_db: ya_models.OrderItemPrice = self.db_session.query(ya_models.OrderItemPrice).filter(
            ya_models.OrderItemPrice.order_item_id == order_item_price_model.order_item_id,
            ya_models.OrderItemPrice.price_type == order_item_price_model.price_type
        ).first()

        try:    
            assert order_item_price_in_db.cost_per_item == order_item_price_model.cost_per_item, f"This attribute {order_item_price_in_db.cost_per_item} doesn't match with those from API ({order_item_price_model.cost_per_item}) for this order ({order_item_price_model.order_item_id})"
            assert order_item_price_in_db.total == order_item_price_model.total, f"This attribute {order_item_price_in_db.total} doesn't match with those from API ({order_item_price_model.total}) for this order ({order_item_price_model.order_item_id})"
        except AssertionError as e:
            print(e)

        self.db_session.commit()

    def create(self, order_item_price_model: ya_models.OrderItemPrice) -> None:
        """Creates Order entity"""
        self.db_session.add(order_item_price_model)
        self.db_session.commit()

    def refresh(self, order_item_price_schema: dict) -> None:
        order_item_price_model_ = self.prep_model(schema_=order_item_price_schema)
        if self.check_integrity(order_item_price_model=order_item_price_model_):
            self.update(order_item_price_model=order_item_price_model_)
            return None
        self.create(order_item_price_model=order_item_price_model_)
        return None
    

class DBOrderItemsDetailsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: ClientSession,
            db_session, db_engine
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
        if order_queried.count() == 0:
            print(f"This order {schema_['order_id']} for this supplier ( {self.sesh.supplier.id} ) doesn't have a represantiton in db")
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

    def get_order_item_id(self, schema_: dict) -> int:
        order_item_queried = self.db_session.query(ya_models.OrderItem).filter(
            ya_models.OrderItem.shop_sku_id == int(schema_['shop_sku_id']),
            ya_models.OrderItem.order_id == int(schema_['order_id'])
        )
        if order_item_queried.count() > 1:
            print(f"This order item with order id {schema_['order_id']}, {schema_['shop_sku']} for this supplier ( {self.sesh.supplier.id} ) has duplicate ids in db")
        order_item_in_db = order_item_queried.first()
        if order_item_in_db:
            return order_item_in_db.id
        else:
            print(f"FATAL error -> this shop sku can't be found {schema_['shop_sku']}")

    def prep_model(self, schema_: dict) -> ya_models.OrderItemDetails:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in ya_models.OrderItemDetails.__dict__ if not i.startswith('_')]
        # order_schema: dict[str, Any] = schema_.to_dict()

        order_item_details_schema = schema_
        # order_item_details_schema['order_id'] = self.get_order_id(schema_=schema_)
        order_item_details_schema['shop_sku_id'] = self.get_shop_sku_id(schema_=schema_)
        order_item_details_schema['order_item_id'] = self.get_order_item_id(schema_=order_item_details_schema)
        order_item_details_schema['price_type'] = order_item_details_schema['type']
        
        order_item_details_schema = {key: value for key, value in order_item_details_schema.items() if key in req_fields}
        return ya_models.OrderItemDetails(**order_item_details_schema)
    
    def check_integrity(self, order_item_price_model: ya_models.OrderItemDetails) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_items_in_db: ya_models.OrderItemDetails = self.db_session.query(ya_models.OrderItemDetails).filter(
            ya_models.OrderItemDetails.order_item_id == order_item_price_model.order_item_id,
            ya_models.OrderItemDetails.price_type == order_item_price_model.price_type
        )
        if order_items_in_db.count() > 1:
            print(f"This order item with id - {order_item_price_model.order_item_id} for this price type ({order_item_price_model.price_type}) has duplicates")
        order_items_in_db = order_items_in_db.first()
        if order_items_in_db:
            return True
        return False
    
    def update(self, order_item_price_model: ya_models.OrderItemDetails) -> None:
        """Updates Product entity"""
        order_item_price_in_db: ya_models.OrderItemDetails = self.db_session.query(ya_models.OrderItemDetails).filter(
            ya_models.OrderItemDetails.order_item_id == order_item_price_model.order_item_id,
            ya_models.OrderItemDetails.price_type == order_item_price_model.price_type
        ).first()

        try:    
            assert order_item_price_in_db.cost_per_item == order_item_price_model.cost_per_item, f"This attribute {order_item_price_in_db.cost_per_item} doesn't match with those from API ({order_item_price_model.cost_per_item}) for this order ({order_item_price_model.order_item_id})"
            assert order_item_price_in_db.total == order_item_price_model.total, f"This attribute {order_item_price_in_db.total} doesn't match with those from API ({order_item_price_model.total}) for this order ({order_item_price_model.order_item_id})"
        except AssertionError as e:
            print(e)

        self.db_session.commit()

    def create(self, order_item_price_model: ya_models.OrderItemDetails) -> None:
        """Creates Order entity"""
        self.db_session.add(order_item_price_model)
        self.db_session.commit()

    def refresh(self, order_item_details_schema: dict) -> None:
        order_item_price_model_ = self.prep_model(schema_=order_item_details_schema)
        if self.check_integrity(order_item_price_model=order_item_price_model_):
            self.update(order_item_price_model=order_item_price_model_)
            return None
        self.create(order_item_price_model=order_item_price_model_)
        return None