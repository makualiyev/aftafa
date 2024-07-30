from datetime import datetime, date, timedelta
from typing import Optional, Any, Union

from sqlalchemy import func
from requests import Session

from aftafa.client.megamarket.client import PRIVATE_MERCHANTS
from aftafa.client.megamarket.models import engine, session as db_session
import aftafa.client.megamarket.models as sbermm_models
from aftafa.client.megamarket.schemas.catalog_item import CatalogItem
from aftafa.client.megamarket.schemas.order_search_item import OrderSearchItem
from aftafa.client.megamarket.schemas.merchant import MerchantItem
from aftafa.client.megamarket.schemas.stock import StockItem
from aftafa.client.megamarket.crud_base import merchant_goods as merchant_goods_crud
from aftafa.client.megamarket.crud_base import suggested_goods as suggested_goods_crud
from aftafa.client.megamarket.crud_base import order_items as order_items_crud
from aftafa.client.megamarket.client import ApiClient


class DBCatalogUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: CatalogItem) -> sbermm_models.CatalogItem:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.CatalogItem.__dict__ if not i.startswith("_")
        ]
        catalog_item_schema: dict[str, Any] = schema_.to_dict()
        main_catalog_item_schema = catalog_item_schema["main_catalog_item"]

        main_catalog_item_schema = {
            key: value
            for key, value in main_catalog_item_schema.items()
            if key in req_fields
        }

        return sbermm_models.CatalogItem(**main_catalog_item_schema)

    def check_integrity(
        self, main_catalog_item_model: sbermm_models.CatalogItem
    ) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        main_catalog_item_queried: sbermm_models.CatalogItem = self.db_session.query(
            sbermm_models.CatalogItem
        ).filter(
            sbermm_models.CatalogItem.catalog_item_id
            == str(main_catalog_item_model.catalog_item_id)
        )
        if main_catalog_item_queried.count() > 1:
            print(
                f"This order entry {main_catalog_item_model.catalog_item_id} has duplicates"
            )
        main_catalog_item_in_db = main_catalog_item_queried.first()
        if main_catalog_item_in_db:
            return True
        return False

    def update(self, main_catalog_item_model: sbermm_models.CatalogItem) -> None:
        """Updates Product entity"""
        main_catalog_item_in_db: sbermm_models.CatalogItem = (
            self.db_session.query(sbermm_models.CatalogItem)
            .filter(
                sbermm_models.CatalogItem.catalog_item_id
                == str(main_catalog_item_model.catalog_item_id)
            )
            .first()
        )

        main_catalog_item_in_db.date_confirmation = (
            main_catalog_item_model.date_confirmation
        )
        main_catalog_item_in_db.publication_status = (
            main_catalog_item_model.publication_status
        )
        main_catalog_item_in_db.publication_status_humanized = (
            main_catalog_item_model.publication_status_humanized
        )
        main_catalog_item_in_db.quantity = main_catalog_item_model.quantity

        self.db_session.commit()

    def create(self, main_catalog_item_model: sbermm_models.CatalogItem) -> None:
        """Creates Order entity"""
        self.db_session.add(main_catalog_item_model)
        self.db_session.commit()

    def populate_catalog_item(self, schema_: CatalogItem) -> None:
        catalog_item_schema: dict[str, Any] = schema_.to_dict()

        if catalog_item_schema.get("merchant_goods")[0]:
            DBMerchantGoodsUpdater(client_session=self.sesh).refresh(
                merchant_goods_schema=catalog_item_schema
            )
        if catalog_item_schema.get("suggested_goods")[0]:
            DBSuggestedGoodsUpdater(client_session=self.sesh).refresh(
                suggested_goods_schema=catalog_item_schema
            )

    #         if catalog_item_schema.get('payments')[0]:
    #             for payment_entry in catalog_item_schema.get('payments')[1]:
    #                 DBOrderPaymentsUpdater(client_session=self.sesh).refresh(
    #                     order_payment_schema=payment_entry
    #                 )
    #         if catalog_item_schema.get('items')[0]:
    #             for order_item_entry in catalog_item_schema.get('items')[1]:
    #                 DBOrderItemsUpdater(client_session=self.sesh).refresh(
    #                     order_item_schema=order_item_entry
    #                 )
    #         if catalog_item_schema.get('initial_items')[0]:
    #             for order_item_entry in catalog_item_schema.get('initial_items')[1]:
    #                 DBOrderItemsUpdater(client_session=self.sesh).refresh(
    #                     order_item_schema=order_item_entry
    #                 )

    def refresh(self, main_catalog_item_schema_: dict) -> None:
        main_catalog_item_model_ = self.prep_model(schema_=main_catalog_item_schema_)
        if self.check_integrity(main_catalog_item_model=main_catalog_item_model_):
            self.update(main_catalog_item_model=main_catalog_item_model_)
            return None
        self.create(main_catalog_item_model=main_catalog_item_model_)
        return None


class DBSuggestListUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: CatalogItem) -> sbermm_models.CatalogItem:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.CatalogItem.__dict__ if not i.startswith("_")
        ]
        catalog_item_schema: dict[str, Any] = schema_.to_dict()
        main_catalog_item_schema = catalog_item_schema["main_catalog_item"]

        main_catalog_item_schema = {
            key: value
            for key, value in main_catalog_item_schema.items()
            if key in req_fields
        }

        return sbermm_models.CatalogItem(**main_catalog_item_schema)

    def check_integrity(
        self, main_catalog_item_model: sbermm_models.CatalogItem
    ) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        main_catalog_item_queried: sbermm_models.CatalogItem = self.db_session.query(
            sbermm_models.CatalogItem
        ).filter(
            sbermm_models.CatalogItem.catalog_item_id
            == str(main_catalog_item_model.catalog_item_id)
        )
        if main_catalog_item_queried.count() > 1:
            print(
                f"This order entry {main_catalog_item_model.catalog_item_id} has duplicates"
            )
        main_catalog_item_in_db = main_catalog_item_queried.first()
        if main_catalog_item_in_db:
            return True
        return False

    def update(self, main_catalog_item_model: sbermm_models.CatalogItem) -> None:
        """Updates Product entity"""
        main_catalog_item_in_db: sbermm_models.CatalogItem = (
            self.db_session.query(sbermm_models.CatalogItem)
            .filter(
                sbermm_models.CatalogItem.catalog_item_id
                == str(main_catalog_item_model.catalog_item_id)
            )
            .first()
        )

        main_catalog_item_in_db.date_confirmation = (
            main_catalog_item_model.date_confirmation
        )
        main_catalog_item_in_db.publication_status = (
            main_catalog_item_model.publication_status
        )
        main_catalog_item_in_db.publication_status_humanized = (
            main_catalog_item_model.publication_status_humanized
        )
        main_catalog_item_in_db.quantity = main_catalog_item_model.quantity

        self.db_session.commit()

    def create(self, main_catalog_item_model: sbermm_models.CatalogItem) -> None:
        """Creates Order entity"""
        self.db_session.add(main_catalog_item_model)
        self.db_session.commit()

    def populate_catalog_item(self, schema_: CatalogItem) -> None:
        catalog_item_schema: dict[str, Any] = schema_.to_dict()

        if catalog_item_schema.get("merchant_goods")[0]:
            DBMerchantGoodsUpdater(client_session=self.sesh).refresh(
                merchant_goods_schema=catalog_item_schema
            )

    def refresh(self, main_catalog_item_schema_: dict) -> None:
        main_catalog_item_model_ = self.prep_model(schema_=main_catalog_item_schema_)
        if self.check_integrity(main_catalog_item_model=main_catalog_item_model_):
            self.update(main_catalog_item_model=main_catalog_item_model_)
            return None
        self.create(main_catalog_item_model=main_catalog_item_model_)
        return None
    

class DBMerchantGoodsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_catalog_item_id(self, schema_: dict) -> int:
        """gets order_id"""
        catalog_item_queried: sbermm_models.CatalogItem = self.db_session.query(
            sbermm_models.CatalogItem
        ).filter(
            sbermm_models.CatalogItem.catalog_item_id
            == str(schema_.get('main_catalog_item').get("catalog_item_id"))
        )
        if catalog_item_queried.count() > 1:
            print(
                f"This order {schema_.get('main_catalog_item').get('catalog_item_id')} has duplicate ids in db"
            )
        catalog_item_in_db = catalog_item_queried.first()
        if catalog_item_in_db:
            return catalog_item_in_db.id

    def prep_model(self, schema_: dict) -> sbermm_models.MerchantGoods:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [
            i for i in sbermm_models.MerchantGoods.__dict__ if not i.startswith("_")
        ]

        merchant_goods_schema = schema_.get("merchant_goods")[1]
        merchant_goods_schema["catalog_item_id"] = self.get_catalog_item_id(
            schema_=schema_
        )
        if not merchant_goods_schema["currency_id"]:
            merchant_goods_schema["currency_id"] = "RUR"
        if not merchant_goods_schema.get('category_id'):
            merchant_goods_schema['category_id'] = 0
        merchant_goods_schema = {
            key: value
            for key, value in merchant_goods_schema.items()
            if key in req_fields
        }
        merchant_goods_schema['merchant_goods_id'] = schema_.get('main_catalog_item').get("catalog_item_id")
        return sbermm_models.MerchantGoods(**merchant_goods_schema)

    def check_integrity(
        self, merchant_goods_model: sbermm_models.MerchantGoods
    ) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        merchant_goods_queried: sbermm_models.MerchantGoods = self.db_session.query(
            sbermm_models.MerchantGoods
        ).filter(
            sbermm_models.MerchantGoods.catalog_item_id
            == int(merchant_goods_model.catalog_item_id)
        )
        if merchant_goods_queried.count() > 1:
            print(
                f"This merchant goods {merchant_goods_model.merchant_offer_id} has duplicates"
            )
        merchant_goods_in_db = merchant_goods_queried.first()
        if merchant_goods_in_db:
            return True
        return False

    def update(self, merchant_goods_model: sbermm_models.MerchantGoods) -> None:
        """Updates Product entity"""
        merchant_goods_in_db: sbermm_models.MerchantGoods = (
            self.db_session.query(sbermm_models.MerchantGoods)
            .filter(
                sbermm_models.MerchantGoods.catalog_item_id
                == str(merchant_goods_model.catalog_item_id)
            )
            .first()
        )

        merchant_goods_in_db.delivery = merchant_goods_model.delivery
        merchant_goods_in_db.pickup = merchant_goods_model.pickup
        merchant_goods_in_db.store = merchant_goods_model.store
        merchant_goods_in_db.url = merchant_goods_model.url
        merchant_goods_in_db.picture = merchant_goods_model.picture
        merchant_goods_in_db.name = merchant_goods_model.name
        merchant_goods_in_db.merchant_offer_name = (
            merchant_goods_model.merchant_offer_name
        )
        merchant_goods_in_db.barcode = merchant_goods_model.barcode
        merchant_goods_in_db.vendor = merchant_goods_model.vendor
        merchant_goods_in_db.vendor_code = merchant_goods_model.vendor_code
        merchant_goods_in_db.category_id = merchant_goods_model.category_id
        merchant_goods_in_db.category_path = merchant_goods_model.category_path
        merchant_goods_in_db.currency_id = merchant_goods_model.currency_id
        merchant_goods_in_db.price = merchant_goods_model.price

        self.db_session.commit()

    def create(self, merchant_goods_model: sbermm_models.MerchantGoods) -> None:
        """Creates Order entity"""
        self.db_session.add(merchant_goods_model)
        self.db_session.commit()

    def refresh(self, merchant_goods_schema: dict) -> None:
        merchant_goods_model_ = self.prep_model(schema_=merchant_goods_schema)
        if self.check_integrity(merchant_goods_model=merchant_goods_model_):
            self.update(merchant_goods_model=merchant_goods_model_)
            self.populate_merchant_goods(schema_=merchant_goods_schema)
            return None
        self.create(merchant_goods_model=merchant_goods_model_)
        self.populate_merchant_goods(schema_=merchant_goods_schema)
        return None

    def populate_merchant_goods(self, schema_: dict) -> None:
        # order_item_schema: dict[str, Any] = schema_.to_dict()
        merchant_goods_schema: dict[str, Any] = schema_

        if merchant_goods_schema.get("merchant_goods_outlets")[0]:
            for merchant_goods_outlet_schema in merchant_goods_schema[
                "merchant_goods_outlets"
            ][1]:
                merchant_goods_crud.DBMerchantGoodsOutletsUpdater(
                    client_session=self.sesh,
                    db_session=self.db_session,
                    db_engine=self.db_engine,
                ).refresh(merchant_goods_outlet_schema=merchant_goods_outlet_schema)


class DBSuggestedGoodsUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_catalog_item_id(self, schema_: dict) -> int:
        """gets order_id"""
        catalog_item_queried: sbermm_models.CatalogItem = self.db_session.query(
            sbermm_models.CatalogItem
        ).filter(
            sbermm_models.CatalogItem.catalog_item_id
            == str(schema_.get("main_catalog_item").get("catalog_item_id"))
        )
        if catalog_item_queried.count() > 1:
            print(
                f"This catalog item {schema_.get('main_catalog_item').get('catalog_item_id')} has duplicate ids in db"
            )
        catalog_item_in_db = catalog_item_queried.first()
        if catalog_item_in_db:
            return catalog_item_in_db.id

    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoods:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [
            i for i in sbermm_models.SuggestedGoods.__dict__ if not i.startswith("_")
        ]

        suggested_goods_schema = schema_.get("suggested_goods")[1]
        suggested_goods_schema["catalog_item_id"] = self.get_catalog_item_id(
            schema_=schema_
        )
        suggested_goods_schema["suggested_goods_id"] = schema_.get('main_catalog_item').get('catalog_item_id')
        if not suggested_goods_schema.get("publication_date"):
            suggested_goods_schema["publication_date"] = None
        suggested_goods_schema = {
            key: value
            for key, value in suggested_goods_schema.items()
            if key in req_fields
        }
        return sbermm_models.SuggestedGoods(**suggested_goods_schema)

    def check_integrity(
        self, suggested_goods_model: sbermm_models.SuggestedGoods
    ) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_queried: sbermm_models.SuggestedGoods = self.db_session.query(
            sbermm_models.SuggestedGoods
        ).filter(
            sbermm_models.SuggestedGoods.catalog_item_id
            == int(suggested_goods_model.catalog_item_id)
        )
        if suggested_goods_queried.count() > 1:
            print(
                f"This merchant goods {suggested_goods_model.goods_id} has duplicates"
            )
        suggested_goods_in_db = suggested_goods_queried.first()
        if suggested_goods_in_db:
            return True
        return False

    def update(self, suggested_goods_model: sbermm_models.SuggestedGoods) -> None:
        """Updates Product entity"""
        suggested_goods_in_db: sbermm_models.SuggestedGoods = (
            self.db_session.query(sbermm_models.SuggestedGoods)
            .filter(
                sbermm_models.SuggestedGoods.catalog_item_id
                == int(suggested_goods_model.catalog_item_id)
            )
            .first()
        )

        suggested_goods_in_db.rate = suggested_goods_model.rate
        suggested_goods_in_db.date_activate = suggested_goods_model.date_activate
        suggested_goods_in_db.single_offer_card = (
            suggested_goods_model.single_offer_card
        )
        suggested_goods_in_db.short_web_name = suggested_goods_model.short_web_name
        suggested_goods_in_db.brand = suggested_goods_model.brand
        suggested_goods_in_db.brand_slug = suggested_goods_model.brand_slug
        suggested_goods_in_db.gtin = suggested_goods_model.gtin
        suggested_goods_in_db.logistic_class = suggested_goods_model.logistic_class
        suggested_goods_in_db.logistic_class_code = (
            suggested_goods_model.logistic_class_code
        )
        suggested_goods_in_db.logistic_class_type = (
            suggested_goods_model.logistic_class_type
        )
        suggested_goods_in_db.manufacturer_part_no = (
            suggested_goods_model.manufacturer_part_no
        )
        suggested_goods_in_db.model = suggested_goods_model.model
        suggested_goods_in_db.multiboxes_possible = (
            suggested_goods_model.multiboxes_possible
        )
        suggested_goods_in_db.nds = suggested_goods_model.nds
        suggested_goods_in_db.flags = suggested_goods_model.flags
        suggested_goods_in_db.update_at = suggested_goods_model.update_at
        suggested_goods_in_db.publication_date = suggested_goods_model.publication_date
        suggested_goods_in_db.url = suggested_goods_model.url
        suggested_goods_in_db.reviews_count = suggested_goods_model.reviews_count
        suggested_goods_in_db.reviews_rating = suggested_goods_model.reviews_rating
        suggested_goods_in_db.reviews_show = suggested_goods_model.reviews_show
        suggested_goods_in_db.quality = suggested_goods_model.quality
        suggested_goods_in_db.category_master = suggested_goods_model.category_master
        

        self.db_session.commit()

    def create(self, suggested_goods_model: sbermm_models.SuggestedGoods) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_model)
        self.db_session.commit()

    def refresh(self, suggested_goods_schema: dict) -> None:
        suggested_goods_model_ = self.prep_model(schema_=suggested_goods_schema)
        if self.check_integrity(suggested_goods_model=suggested_goods_model_):
            self.update(suggested_goods_model=suggested_goods_model_)
            self.populate_suggested_goods(schema_=suggested_goods_schema)
            return None
        self.create(suggested_goods_model=suggested_goods_model_)
        self.populate_suggested_goods(schema_=suggested_goods_schema)
        return None

    def populate_suggested_goods(self, schema_: dict) -> None:
        suggested_goods_schema: dict[str, Any] = schema_

        if suggested_goods_schema.get("suggested_goods_prices")[0]:
            suggested_goods_crud.DBSuggestedGoodsPricesUpdater(
                client_session=self.sesh,
                db_session=self.db_session,
                db_engine=self.db_engine,
            ).refresh(suggested_goods_prices_schema=schema_)
        if suggested_goods_schema.get("suggested_goods_offers_v2")[0]:
            for offer_v2 in suggested_goods_schema.get("suggested_goods_offers_v2")[1]:
                suggested_goods_crud.DBSuggestedGoodsOffersV2Updater(
                        client_session=self.sesh,
                        db_session=self.db_session,
                        db_engine=self.db_engine,
                    ).refresh(suggested_goods_offers_v2_schema=offer_v2)


class DBCategoryUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: CatalogItem) -> sbermm_models.Category:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.Category.__dict__ if not i.startswith("_")
        ]
        category_schema: dict[str, Any] = schema_
        category_schema["category_id"] = int(category_schema["category_id"])
        if category_schema["parent_category_id"]:
            category_schema["parent_category_id"] = int(
                category_schema["parent_category_id"]
            )

        category_schema["parent_id"] = category_schema["parent_category_id"]
        category_schema = {
            key: value for key, value in category_schema.items() if key in req_fields
        }

        return sbermm_models.Category(**category_schema)

    def check_integrity(self, category_model: sbermm_models.Category) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        category_queried: sbermm_models.Category = self.db_session.query(
            sbermm_models.Category
        ).filter(sbermm_models.Category.category_id == int(category_model.category_id))
        if category_queried.count() > 1:
            print(f"This category entry {category_model.category_id} has duplicates")
        category_in_db = category_queried.first()
        if category_in_db:
            return True
        return False

    def update(self, category_model: sbermm_models.Category) -> None:
        """Updates Product entity"""
        category_in_db: sbermm_models.Category = (
            self.db_session.query(sbermm_models.Category)
            .filter(
                sbermm_models.Category.category_id == int(category_model.category_id)
            )
            .first()
        )

        category_in_db.name = category_model.name
        category_in_db.structure_id = category_model.structure_id
        category_in_db.parent_id = category_model.parent_id

        self.db_session.commit()

    def create(self, category_model: sbermm_models.Category) -> None:
        """Creates Order entity"""
        self.db_session.add(category_model)
        self.db_session.commit()

    def refresh(self, category_schema_: dict) -> None:
        category_model_ = self.prep_model(schema_=category_schema_)
        if self.check_integrity(category_model=category_model_):
            self.update(category_model=category_model_)
            return None
        self.create(category_model=category_model_)
        return None


class DBSearchOrderUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: OrderSearchItem) -> sbermm_models.Order:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.Order.__dict__ if not i.startswith("_")
        ]
        search_order_schema: dict[str, Any] = schema_.to_dict(merchant_id=self.sesh._merchant_id)
        main_search_order_schema = search_order_schema["order_main"]

        main_search_order_schema = {
            key: value
            for key, value in main_search_order_schema.items()
            if key in req_fields
        }

        return sbermm_models.Order(**main_search_order_schema)      

    def check_integrity(self, search_order_model: sbermm_models.Order) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        search_order_queried: sbermm_models.Order = self.db_session.query(
            sbermm_models.Order
        ).filter(
            sbermm_models.Order.uid == search_order_model.uid
        )
        if search_order_queried.count() > 1:
            print(f"This search_order entry {search_order_model.uid} has duplicates")
        search_order_in_db = search_order_queried.first()
        if search_order_in_db:
            return True
        return False

    def update(self, search_order_model: sbermm_models.Order) -> None:
        """Updates Product entity"""
        search_order_in_db: sbermm_models.Order = (
            self.db_session.query(sbermm_models.Order)
            .filter(
                sbermm_models.Order.uid == search_order_model.uid
            )
            .first()
        )

        search_order_in_db.order_code = search_order_model.order_code

        self.db_session.commit()

    def create(self, search_order_model: sbermm_models.Order) -> None:
        """Creates Order entity"""
        self.db_session.add(search_order_model)
        self.db_session.commit()

    def populate_order_items(self, schema_: OrderSearchItem) -> None:
        order_item_schema: dict[str, Any] = schema_.to_dict(merchant_id=self.sesh._merchant_id)

        if order_item_schema.get("order_items")[0]:
            for order_item in order_item_schema.get("order_items")[1]:
                order_items_crud.DBOrderItemsUpdater(
                            client_session=self.sesh,
                            db_session=self.db_session,
                            db_engine=self.db_engine
                    ).refresh(
                            order_item_schema_=order_item
                        )
    
    def refresh(self, search_order_schema_: dict) -> None:
        search_order_model_ = self.prep_model(schema_=search_order_schema_)
        if self.check_integrity(search_order_model=search_order_model_):
            self.update(search_order_model=search_order_model_)
            return None
        self.create(search_order_model=search_order_model_)
        return None
    

class DBMerchantInfoUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_slug_from_db(self, merchant_id: int) -> str:
        queried_merchant: sbermm_models.Merchant = self.db_session.query(sbermm_models.Merchant).filter(
                                        sbermm_models.Merchant.id == merchant_id
                                    ).first()
        return queried_merchant.slug
    
    def get_account_id_from_db(self, merchant_id: int) -> int:
        queried_merchant: sbermm_models.Merchant = self.db_session.query(sbermm_models.Merchant).filter(
                                        sbermm_models.Merchant.id == merchant_id
                                    ).first()
        return queried_merchant.account_id

    def prep_model(self, schema_: MerchantItem) -> sbermm_models.MerchantInfo:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.MerchantInfo.__dict__ if not i.startswith("_")
        ]
        merchant_info_schema: dict[str, Any] = schema_.dict()
        merchant_info_schema['account_id'] = self.get_account_id_from_db(merchant_id=merchant_info_schema['merchant_id'])
        merchant_info_schema['slug'] = self.get_slug_from_db(merchant_id=merchant_info_schema['merchant_id'])
        merchant_info_schema = {
            key: value for key, value in merchant_info_schema.items() if key in req_fields
        }

        return sbermm_models.MerchantInfo(**merchant_info_schema)

    def check_integrity(self, merchant_info_model: sbermm_models.MerchantInfo) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        merchant_info_queried: sbermm_models.MerchantInfo = self.db_session.query(
                                                        sbermm_models.MerchantInfo
                                                    ).filter(
                                                        sbermm_models.MerchantInfo.merchant_id == merchant_info_model.merchant_id
                                                    )
        if merchant_info_queried.count() > 1:
            print(f"This merchant_info entry {merchant_info_model.merchant_info_id} has duplicates")
        merchant_info_in_db = merchant_info_queried.first()
        if merchant_info_in_db:
            return True
        return False

    def update(self, merchant_info_model: sbermm_models.MerchantInfo) -> None:
        """Updates Product entity"""
        merchant_info_in_db: sbermm_models.MerchantInfo = (
            self.db_session.query(sbermm_models.MerchantInfo)
            .filter(
                sbermm_models.MerchantInfo.merchant_id == merchant_info_model.merchant_id
            )
            .first()
        )

        for attr_pair in [(k, v) for k, v in merchant_info_model.__dict__.items() if not k.startswith('_')]:
                merchant_info_in_db.__setattr__(attr_pair[0], attr_pair[1])
                # merchant_info_in_db.__setattr__(attr_pair[0], merchant_info_model.__getattribute__(attr_))

        self.db_session.commit()

    def create(self, merchant_info_model: sbermm_models.MerchantInfo) -> None:
        """Creates Order entity"""
        self.db_session.add(merchant_info_model)
        self.db_session.commit()

    def refresh(self, merchant_info_schema_: dict) -> None:
        merchant_info_model_ = self.prep_model(schema_=merchant_info_schema_)
        if self.check_integrity(merchant_info_model=merchant_info_model_):
            self.update(merchant_info_model=merchant_info_model_)
            return None
        self.create(merchant_info_model=merchant_info_model_)
        return None
    

class DBStockUpdater:
    """
    Updater for offer mappings from Yandex Market
    """

    ...

    def __init__(
        self, client_session: Session, db_session=db_session, db_engine=engine,
        extraction_ts: datetime | None = None
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session
        if not extraction_ts:
            self.random_ts = datetime.now()
        else:
            self.random_ts = extraction_ts
        
    def get_catalog_item_id(self, schema_: dict) -> int:
        """gets order_id"""
        catalog_item_queried: sbermm_models.CatalogItem = self.db_session.query(
            sbermm_models.CatalogItem
        ).filter(
            sbermm_models.CatalogItem.catalog_item_id == '-'.join([str(schema_.get('merchant_id')), schema_.get("item_id")])
        )
        if catalog_item_queried.count() > 1:
            print(
                f"This item {schema_.get('item_id')} has duplicate ids in db"
            )
        catalog_item_in_db = catalog_item_queried.first()
        if catalog_item_in_db:
            return catalog_item_in_db.id

    def prep_model(self, schema_: dict[str, Any]) -> sbermm_models.Stock:
        """prepares ORM model for a given schema"""

        req_fields: list[str] = [
            i for i in sbermm_models.Stock.__dict__ if not i.startswith("_")
        ]
        schema_['merchant_id'] = self.sesh._merchant_id
        schema_['catalog_item_id'] = self.get_catalog_item_id(schema_=schema_)
        schema_['extracted_at'] = self.random_ts
        stock_schema = {
            key: value for key, value in schema_.items() if key in req_fields
        }

        return sbermm_models.Stock(**stock_schema)

    def check_integrity(self, stock_model: sbermm_models.Stock) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        stock_queried: sbermm_models.Stock = self.db_session.query(
                                                        sbermm_models.Stock
                                                    ).filter(
                                                        sbermm_models.Stock.merchant_id == stock_model.merchant_id,
                                                        sbermm_models.Stock.catalog_item_id == stock_model.catalog_item_id,
                                                        sbermm_models.Stock.facility_id == stock_model.facility_id,
                                                        sbermm_models.Stock.fact_quality == stock_model.fact_quality,
                                                        func.date(sbermm_models.Stock.extracted_at) == datetime.today().date()
                                                    )
        if stock_queried.count() > 1:
            print(f"This stock entry {stock_model.stock_id} has duplicates")
        stock_in_db = stock_queried.first()
        if stock_in_db:
            return True
        return False

    def update(self, stock_model: sbermm_models.Stock) -> None:
        """Updates Product entity"""
        stock_in_db: sbermm_models.Stock = (
            self.db_session.query(sbermm_models.Stock)
            .filter(
                sbermm_models.Stock.merchant_id == stock_model.merchant_id,
                sbermm_models.Stock.catalog_item_id == stock_model.catalog_item_id,
                sbermm_models.Stock.facility_id == stock_model.facility_id,
                sbermm_models.Stock.fact_quality == stock_model.fact_quality,
                func.date(sbermm_models.Stock.extracted_at) == datetime.today().date()
            )
            .first()
        )
        not_updated_cols = [
            'id',
            'merchant_id',
            'catalog_item_id',
            'item_id',
            'facility_id'
            'fact_quality',
            'extracted_at'
        ]

        for attr_pair in [(k, v) for k, v in stock_model.__dict__.items() if not k.startswith('_') and not k in not_updated_cols]:
                stock_in_db.__setattr__(attr_pair[0], attr_pair[1])
        stock_in_db.updated_at = self.random_ts

        self.db_session.commit()

    def create(self, stock_model: sbermm_models.Stock) -> None:
        """Creates Order entity"""
        self.db_session.add(stock_model)
        self.db_session.commit()

    def refresh(self, stock_schema_: dict) -> None:
        for stock_entry in stock_schema_.to_dict():
            stock_model_ = self.prep_model(schema_=stock_entry)
            if self.check_integrity(stock_model=stock_model_):
                self.update(stock_model=stock_model_)
                return None
            self.create(stock_model=stock_model_)
            return None
    