from requests import Session

import aftafa.client.megamarket.models as sbermm_models


class DBOrderItemDiscountsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    ...
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: dict) -> sbermm_models.OrderItemDiscount:
        """prepares ORM model for a given schema"""
        
        req_fields: list[str] = [i for i in sbermm_models.OrderItemDiscount.__dict__ if not i.startswith('_')]
        order_item_discount_schema = {key: value for key, value in schema_.items() if key in req_fields}
        
        return sbermm_models.OrderItemDiscount(**order_item_discount_schema)
    
    def check_integrity(self, order_item_discount_model: sbermm_models.OrderItemDiscount) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_item_discount_queried: sbermm_models.OrderItemDiscount = self.db_session.query(sbermm_models.OrderItemDiscount).filter(
            sbermm_models.OrderItemDiscount.order_position_id == order_item_discount_model.order_position_id,
            sbermm_models.OrderItemDiscount.discount_type == order_item_discount_model.discount_type
        )
        if order_item_discount_queried.count() > 1:
            print(f"This order_item_discount - {order_item_discount_model.id} - has duplicates")
        order_item_discount_in_db = order_item_discount_queried.first()
        if order_item_discount_in_db:
            return True
        return False
    
    def update(self, order_item_discount_model: sbermm_models.OrderItemDiscount) -> None:
        """Updates Product entity"""
        order_item_discount_in_db: sbermm_models.OrderItemDiscount = self.db_session.query(sbermm_models.OrderItemDiscount).filter(
            sbermm_models.OrderItemDiscount.order_position_id == order_item_discount_model.order_position_id,
            sbermm_models.OrderItemDiscount.discount_type == order_item_discount_model.discount_type
        ).first()

        order_item_discount_in_db.discount_description = order_item_discount_model.discount_description
        order_item_discount_in_db.discount_amount = order_item_discount_model.discount_amount

        self.db_session.commit()

    def create(self, order_item_discount_model: sbermm_models.OrderItemDiscount) -> None:
        """Creates Order entity"""
        self.db_session.add(order_item_discount_model)
        self.db_session.commit()


    def refresh(self, order_item_discount_schema_: dict) -> None:
        order_item_discount_model_ = self.prep_model(schema_=order_item_discount_schema_)
        if self.check_integrity(order_item_discount_model=order_item_discount_model_):
            self.update(order_item_discount_model=order_item_discount_model_)
            return None
        self.create(order_item_discount_model=order_item_discount_model_)
        return None


class DBOrderItemsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    ...
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: dict) -> sbermm_models.OrderItem:
        """prepares ORM model for a given schema"""
        
        req_fields: list[str] = [i for i in sbermm_models.OrderItem.__dict__ if not i.startswith('_')]
        order_item_schema = {key: value for key, value in schema_.items() if key in req_fields}
        
        return sbermm_models.OrderItem(**order_item_schema)
    
    def check_integrity(self, order_item_model: sbermm_models.OrderItem) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_item_queried: sbermm_models.OrderItem = self.db_session.query(sbermm_models.OrderItem).filter(
            sbermm_models.OrderItem.order_position_id == order_item_model.order_position_id
        )
        if order_item_queried.count() > 1:
            print(f"This order_item - {order_item_model.id} - has duplicates")
        order_item_in_db = order_item_queried.first()
        if order_item_in_db:
            return True
        return False
    
    def update(self, order_item_model: sbermm_models.OrderItem) -> None:
        """Updates Product entity"""
        order_item_in_db: sbermm_models.OrderItem = self.db_session.query(sbermm_models.OrderItem).filter(
            sbermm_models.OrderItem.order_position_id == order_item_model.order_position_id
        ).first()

        order_item_in_db.is_cancelation_pending = order_item_model.is_cancelation_pending
        order_item_in_db.item_index = order_item_model.item_index
        order_item_in_db.status = order_item_model.status
        order_item_in_db.sub_status = order_item_model.sub_status
        order_item_in_db.price = order_item_model.price
        order_item_in_db.final_price = order_item_model.final_price
        order_item_in_db.quantity = order_item_model.quantity
        order_item_in_db.offer_id = order_item_model.offer_id
        order_item_in_db.goods_id = order_item_model.goods_id
        order_item_in_db.digital_mark = order_item_model.digital_mark

        self.db_session.commit()

    def create(self, order_item_model: sbermm_models.OrderItem) -> None:
        """Creates Order entity"""
        self.db_session.add(order_item_model)
        self.db_session.commit()

    def populate_order_items(self, schema_: dict) -> None:
        if schema_.get("discounts"):
            for order_item_discount in schema_.get("discounts"):
                DBOrderItemDiscountsUpdater(
                            client_session=self.sesh,
                            db_session=self.db_session,
                            db_engine=self.db_engine
                    ).refresh(
                            order_item_discount_schema_=order_item_discount
                    )

    def refresh(self, order_item_schema_: dict) -> None:
        order_item_model_ = self.prep_model(schema_=order_item_schema_)
        if self.check_integrity(order_item_model=order_item_model_):
            self.update(order_item_model=order_item_model_)
            self.populate_order_items(schema_=order_item_schema_)
            return None
        self.create(order_item_model=order_item_model_)
        self.populate_order_items(schema_=order_item_schema_)
        return None


