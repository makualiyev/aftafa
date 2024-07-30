from typing import Any

from requests import Session

import aftafa.client.megamarket.models as sbermm_models
from aftafa.client.megamarket.client import PRIVATE_MERCHANTS


class DBMerchantUpdater:
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

    def prep_model(self, schema_: dict) -> sbermm_models.Merchant:
        """prepares ORM model for a given schema"""
        
        req_fields: list[str] = [i for i in sbermm_models.Merchant.__dict__ if not i.startswith('_')]
        merchant_schema = {key: value for key, value in schema_.items() if key in req_fields}
        if int(merchant_schema['id']) in list(PRIVATE_MERCHANTS.values()):
            merchant_schema['private'] = True
            merchant_schema['account_id'] = 1
        else:
            merchant_schema['private'] = False
        
        return sbermm_models.Merchant(**merchant_schema)
    
    def check_integrity(self, merchant_model: sbermm_models.Merchant) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        merchant_queried: sbermm_models.Merchant = self.db_session.query(sbermm_models.Merchant).filter(
            sbermm_models.Merchant.id == int(merchant_model.id)
        )
        if merchant_queried.count() > 1:
            print(f"This merchant - {merchant_model.id} - has duplicates")
        merchant_in_db = merchant_queried.first()
        if merchant_in_db:
            return True
        return False
    
    def update(self, merchant_model: sbermm_models.Merchant) -> None:
        """Updates Product entity"""
        merchant_in_db: sbermm_models.Merchant = self.db_session.query(sbermm_models.Merchant).filter(
            sbermm_models.Merchant.id == int(merchant_model.id)
        ).first()

        merchant_in_db.name = merchant_model.name

        self.db_session.commit()

    def create(self, merchant_model: sbermm_models.Merchant) -> None:
        """Creates Order entity"""
        self.db_session.add(merchant_model)
        self.db_session.commit()


    def refresh(self, merchant_schema_: dict) -> None:
        merchant_model_ = self.prep_model(schema_=merchant_schema_)
        if self.check_integrity(merchant_model=merchant_model_):
            self.update(merchant_model=merchant_model_)
            return None
        self.create(merchant_model=merchant_model_)
        return None


class DBSuggestedGoodsOffersV2Updater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsOffersV2:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsOffersV2.__dict__ if not i.startswith('_')]

        suggested_goods_offers_v2_schema = schema_
        suggested_goods_offers_v2_schema = {key: value for key, value in suggested_goods_offers_v2_schema.items() if key in req_fields}
        return sbermm_models.SuggestedGoodsOffersV2(**suggested_goods_offers_v2_schema)
    
    def check_integrity(self, suggested_goods_offers_v2_model: sbermm_models.SuggestedGoodsOffersV2) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsOffersV2 = self.db_session.query(sbermm_models.SuggestedGoodsOffersV2).filter(
            sbermm_models.SuggestedGoodsOffersV2.suggested_goods_id == suggested_goods_offers_v2_model.suggested_goods_id,
            sbermm_models.SuggestedGoodsOffersV2.merchant_id == suggested_goods_offers_v2_model.merchant_id
        )
        if suggested_goods_prices_queried.count() > 1:
            print(f"This order item with id - {suggested_goods_offers_v2_model.suggested_goods_id} has duplicates")
        suggested_goods_prices_queried = suggested_goods_prices_queried.first()
        if suggested_goods_prices_queried:
            return True
        return False
    
    def update(self, suggested_goods_offers_v2_model: sbermm_models.SuggestedGoodsOffersV2) -> None:
        """Updates Product entity"""
        suggested_goods_offers_v2_in_db: sbermm_models.SuggestedGoodsOffersV2 = self.db_session.query(sbermm_models.SuggestedGoodsOffersV2).filter(
            sbermm_models.SuggestedGoodsOffersV2.suggested_goods_id == suggested_goods_offers_v2_model.suggested_goods_id,
            sbermm_models.SuggestedGoodsOffersV2.merchant_id == suggested_goods_offers_v2_model.merchant_id
        ).first()

        suggested_goods_offers_v2_in_db.price = suggested_goods_offers_v2_model.price
        suggested_goods_offers_v2_in_db.old_price = suggested_goods_offers_v2_model.old_price
        suggested_goods_offers_v2_in_db.service_scheme = suggested_goods_offers_v2_model.service_scheme
        suggested_goods_offers_v2_in_db.type = suggested_goods_offers_v2_model.type
        suggested_goods_offers_v2_in_db.favorite = suggested_goods_offers_v2_model.favorite
        suggested_goods_offers_v2_in_db.group = suggested_goods_offers_v2_model.group

        self.db_session.commit()

    def create(self, suggested_goods_offers_v2_model: sbermm_models.SuggestedGoodsOffersV2) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_offers_v2_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_offers_v2_schema: dict) -> None:
        suggested_goods_offers_v2_model_ = self.prep_model(schema_=suggested_goods_offers_v2_schema)
        if self.check_integrity(suggested_goods_offers_v2_model=suggested_goods_offers_v2_model_):
            self.update(suggested_goods_offers_v2_model=suggested_goods_offers_v2_model_)
            return None
        self.create(suggested_goods_offers_v2_model=suggested_goods_offers_v2_model_)
        return None


class DBSuggestedGoodsPricesUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPrices:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPrices.__dict__ if not i.startswith('_')]

        suggested_goods_prices_schema = schema_.get('suggested_goods_prices')[1]
        suggested_goods_prices_schema['suggested_goods_id'] = schema_.get('main_catalog_item').get('catalog_item_id')
        suggested_goods_prices_schema = {key: value for key, value in suggested_goods_prices_schema.items() if key in req_fields}
        return sbermm_models.SuggestedGoodsPrices(**suggested_goods_prices_schema)
    
    def check_integrity(self, suggested_goods_prices_model: sbermm_models.SuggestedGoodsPrices) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == suggested_goods_prices_model.suggested_goods_id
        )
        if suggested_goods_prices_queried.count() > 1:
            print(f"This order item with id - {suggested_goods_prices_model.suggested_goods_id} has duplicates")
        suggested_goods_prices_queried = suggested_goods_prices_queried.first()
        if suggested_goods_prices_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_model: sbermm_models.SuggestedGoodsPrices) -> None:
        """Updates Product entity"""
        suggested_goods_prices_in_db: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == suggested_goods_prices_model.suggested_goods_id
        ).first()

        suggested_goods_prices_in_db.is_available = suggested_goods_prices_model.is_available
        suggested_goods_prices_in_db.price_date = suggested_goods_prices_model.price_date
        suggested_goods_prices_in_db.last_price = suggested_goods_prices_model.last_price
        suggested_goods_prices_in_db.final_price = suggested_goods_prices_model.final_price
        suggested_goods_prices_in_db.crossed_price = suggested_goods_prices_model.crossed_price
        suggested_goods_prices_in_db.crossed_price_term = suggested_goods_prices_model.crossed_price_term
        suggested_goods_prices_in_db.min_price = suggested_goods_prices_model.min_price
        suggested_goods_prices_in_db.max_price = suggested_goods_prices_model.max_price
        suggested_goods_prices_in_db.total_offers = suggested_goods_prices_model.total_offers
        suggested_goods_prices_in_db.delivery_date = suggested_goods_prices_model.delivery_date
        suggested_goods_prices_in_db.price_change_percentage = suggested_goods_prices_model.price_change_percentage

        self.db_session.commit()

    def create(self, suggested_goods_prices_model: sbermm_models.SuggestedGoodsPrices) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_schema: dict) -> None:
        suggested_goods_prices_model_ = self.prep_model(schema_=suggested_goods_prices_schema)
        if self.check_integrity(suggested_goods_prices_model=suggested_goods_prices_model_):
            self.update(suggested_goods_prices_model=suggested_goods_prices_model_)
            self.populate_suggested_goods_prices(schema_=suggested_goods_prices_schema)
            return None
        self.create(suggested_goods_prices_model=suggested_goods_prices_model_)
        self.populate_suggested_goods_prices(schema_=suggested_goods_prices_schema)
        return None
    
    def populate_suggested_goods_prices(self, schema_: dict) -> None:
        suggested_goods_schema: dict[str, Any] = schema_
        
        if suggested_goods_schema.get('suggested_goods_prices_favorite_offer')[0]:
            DBSuggestedGoodsPricesFavoriteOfferUpdater(
                client_session=self.sesh,
                db_session=self.db_session,
                db_engine=self.db_engine
            ).refresh(
                suggested_goods_prices_favorite_offer_schema=suggested_goods_schema
            )
        if suggested_goods_schema.get('suggested_goods_prices_offers')[0]:
            for offer_schema in suggested_goods_schema.get('suggested_goods_prices_offers')[1]:
                DBSuggestedGoodsPricesOffersUpdater(
                    client_session=self.sesh,
                    db_session=self.db_session,
                    db_engine=self.db_engine
                ).refresh(
                    suggested_goods_prices_offers_schema=offer_schema
                )
        if suggested_goods_schema.get('suggested_goods_prices_bonus_merchant_bonus')[0]:
            for merchant_bonus in suggested_goods_schema.get('suggested_goods_prices_bonus_merchant_bonus')[1]:
                DBSuggestedGoodsPricesBonusMerchantBonusUpdater(
                    client_session=self.sesh,
                    db_session=self.db_session,
                    db_engine=self.db_engine
                ).refresh(
                    suggested_goods_prices_bonus_merchant_bonus_schema=merchant_bonus
                )
        if suggested_goods_schema.get('suggested_goods_prices_price_history')[0]:
            for price_history_point in suggested_goods_schema.get('suggested_goods_prices_price_history')[1]:
                DBSuggestedGoodsPricesPriceHistoryUpdater(
                    client_session=self.sesh,
                    db_session=self.db_session,
                    db_engine=self.db_engine
                ).refresh(
                    suggested_goods_prices_price_history_schema=price_history_point
                )
        if suggested_goods_schema.get('suggested_goods_prices_price_adjustments')[0]:
            for price_adjustment in suggested_goods_schema.get('suggested_goods_prices_price_adjustments')[1]:
                DBSuggestedGoodsPricesPriceAdjustmentsUpdater(
                    client_session=self.sesh,
                    db_session=self.db_session,
                    db_engine=self.db_engine
                ).refresh(
                    suggested_goods_prices_price_adjustments_schema=price_adjustment
                )




class DBSuggestedGoodsPricesFavoriteOfferUpdater:
    """
    Updater for offer mappings from Yandex Market
    """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_goods_prices_id(self, schema_: dict) -> int:
        """gets order_id"""
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == schema_.get('main_catalog_item').get('catalog_item_id'))
        if suggested_goods_prices_queried.count() > 1:
            print(f"This thing {schema_.get('suggested_goods')[1].get('goods_id')} has duplicate ids in db")
        suggested_goods_prices_in_db = suggested_goods_prices_queried.first()
        if suggested_goods_prices_in_db:
            return suggested_goods_prices_in_db.id
        
    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPricesFavoriteOffer:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesFavoriteOffer.__dict__ if not i.startswith('_')]

        suggested_goods_prices_favorite_offer_schema = schema_.get('suggested_goods_prices_favorite_offer')[1]
        suggested_goods_prices_favorite_offer_schema['goods_prices_id'] = self.get_goods_prices_id(schema_=schema_)
        
        DBMerchantUpdater(
            client_session=self.sesh, db_session=self.db_session, db_engine=self.db_engine
        ).refresh(
            merchant_schema_={
                'id': suggested_goods_prices_favorite_offer_schema['merchant_id'],
                'name': suggested_goods_prices_favorite_offer_schema['merchant_name']
            }
        )

        suggested_goods_prices_favorite_offer_schema = {
            key: value for key, value in suggested_goods_prices_favorite_offer_schema.items() if key in req_fields
        }
        return sbermm_models.SuggestedGoodsPricesFavoriteOffer(
            **suggested_goods_prices_favorite_offer_schema
        )
    
    def check_integrity(self, suggested_goods_prices_favorite_offer_model: sbermm_models.SuggestedGoodsPricesFavoriteOffer) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_favorite_offer_queried: sbermm_models.SuggestedGoodsPricesFavoriteOffer = self.db_session.query(
            sbermm_models.SuggestedGoodsPricesFavoriteOffer
        ).filter(
            sbermm_models.SuggestedGoodsPricesFavoriteOffer.goods_prices_id == suggested_goods_prices_favorite_offer_model.goods_prices_id
        )
        if suggested_goods_prices_favorite_offer_queried.count() > 1:
            print(f"This suggested goods prices with id - {suggested_goods_prices_favorite_offer_model.goods_prices_id} has duplicates")
        suggested_goods_prices_favorite_offer_queried = suggested_goods_prices_favorite_offer_queried.first()
        if suggested_goods_prices_favorite_offer_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_favorite_offer_model: sbermm_models.SuggestedGoodsPricesFavoriteOffer) -> None:
        """Updates Product entity"""
        suggested_goods_prices_favorite_offer_in_db: sbermm_models.SuggestedGoodsPricesFavoriteOffer = self.db_session.query(sbermm_models.SuggestedGoodsPricesFavoriteOffer).filter(
            sbermm_models.SuggestedGoodsPricesFavoriteOffer.goods_prices_id == suggested_goods_prices_favorite_offer_model.goods_prices_id
        ).first()
        
        suggested_goods_prices_favorite_offer_in_db.price = suggested_goods_prices_favorite_offer_model.price
        suggested_goods_prices_favorite_offer_in_db.partner_id = suggested_goods_prices_favorite_offer_model.partner_id
        suggested_goods_prices_favorite_offer_in_db.contract_id = suggested_goods_prices_favorite_offer_model.contract_id
        suggested_goods_prices_favorite_offer_in_db.merchant_id = suggested_goods_prices_favorite_offer_model.merchant_id
        suggested_goods_prices_favorite_offer_in_db.merchant_name = suggested_goods_prices_favorite_offer_model.merchant_name
        suggested_goods_prices_favorite_offer_in_db.old_price = suggested_goods_prices_favorite_offer_model.old_price
        self.db_session.commit()

    def create(self, suggested_goods_prices_favorite_offer_model: sbermm_models.SuggestedGoodsPricesFavoriteOffer) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_favorite_offer_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_favorite_offer_schema: dict) -> None:
        suggested_goods_prices_favorite_offer_model_ = self.prep_model(schema_=suggested_goods_prices_favorite_offer_schema)
        if self.check_integrity(suggested_goods_prices_favorite_offer_model=suggested_goods_prices_favorite_offer_model_):
            self.update(suggested_goods_prices_favorite_offer_model=suggested_goods_prices_favorite_offer_model_)
            # self.populate_suggested_goods_prices_favorite_offer(schema_=suggested_goods_prices_favorite_offer_schema)
            return None
        self.create(suggested_goods_prices_favorite_offer_model=suggested_goods_prices_favorite_offer_model_)
        # self.populate_suggested_goods_prices_favorite_offer(schema_=suggested_goods_prices_favorite_offer_schema)
        return None
    
    # def populate_suggested_goods_prices_favorite_offer(self, schema_: dict) -> None:
    #     suggested_goods_schema: dict[str, Any] = schema_
        
    #     if suggested_goods_schema.get('suggested_goods_prices_favorite_offer')[0]:
    #         suggested_goods_crud.DBSuggestedGoodsPricesUpdater(
    #             client_session=self.sesh,
    #             db_session=self.db_session,
    #             db_engine=self.db_engine
    #         ).refresh(
    #             suggested_goods_prices_favorite_offer_schema=suggested_goods_schema.get('suggested_goods_prices')[1]
    #         )

class DBSuggestedGoodsPricesOffersUpdater:
    """
    Updater for offer mappings from Yandex Market
        """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_goods_prices_id(self, schema_: dict) -> int:
        """gets order_id"""
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == schema_.get('suggested_goods_id'))
        if suggested_goods_prices_queried.count() > 1:
            print(f"This thing {schema_.get('goods_id')} has duplicate ids in db")
        suggested_goods_prices_in_db = suggested_goods_prices_queried.first()
        if suggested_goods_prices_in_db:
            return suggested_goods_prices_in_db.id
        
    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPricesOffers:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesOffers.__dict__ if not i.startswith('_')]

        suggested_goods_prices_offers_schema = schema_
        suggested_goods_prices_offers_schema['goods_prices_id'] = self.get_goods_prices_id(schema_=schema_)
        
        DBMerchantUpdater(
            client_session=self.sesh, db_session=self.db_session, db_engine=self.db_engine
        ).refresh(
            merchant_schema_={
                'id': suggested_goods_prices_offers_schema['merchant_id'],
                'name': suggested_goods_prices_offers_schema['merchant_name']
            }
        )

        suggested_goods_prices_offers_schema = {
            key: value for key, value in suggested_goods_prices_offers_schema.items() if key in req_fields
        }
        return sbermm_models.SuggestedGoodsPricesOffers(
            **suggested_goods_prices_offers_schema
        )
    
    def check_integrity(self, suggested_goods_prices_offers_model: sbermm_models.SuggestedGoodsPricesOffers) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_offers_queried: sbermm_models.SuggestedGoodsPricesOffers = self.db_session.query(
            sbermm_models.SuggestedGoodsPricesOffers
        ).filter(
            sbermm_models.SuggestedGoodsPricesOffers.goods_prices_id == suggested_goods_prices_offers_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesOffers.merchant_id == suggested_goods_prices_offers_model.merchant_id
        )
        if suggested_goods_prices_offers_queried.count() > 1:
            print(f"This suggested goods prices with id - {suggested_goods_prices_offers_model.goods_prices_id} has duplicates")
        suggested_goods_prices_offers_queried = suggested_goods_prices_offers_queried.first()
        if suggested_goods_prices_offers_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_offers_model: sbermm_models.SuggestedGoodsPricesOffers) -> None:
        """Updates Product entity"""
        suggested_goods_prices_offers_in_db: sbermm_models.SuggestedGoodsPricesOffers = self.db_session.query(sbermm_models.SuggestedGoodsPricesOffers).filter(
            sbermm_models.SuggestedGoodsPricesOffers.goods_prices_id == suggested_goods_prices_offers_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesOffers.merchant_id == suggested_goods_prices_offers_model.merchant_id
        ).first()
        
        suggested_goods_prices_offers_in_db.price = suggested_goods_prices_offers_model.price
        suggested_goods_prices_offers_in_db.type = suggested_goods_prices_offers_model.type
    
        self.db_session.commit()

    def create(self, suggested_goods_prices_offers_model: sbermm_models.SuggestedGoodsPricesOffers) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_offers_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_offers_schema: dict) -> None:
        suggested_goods_prices_offers_model_ = self.prep_model(schema_=suggested_goods_prices_offers_schema)
        if self.check_integrity(suggested_goods_prices_offers_model=suggested_goods_prices_offers_model_):
            self.update(suggested_goods_prices_offers_model=suggested_goods_prices_offers_model_)
            # self.populate_suggested_goods_prices_offers(schema_=suggested_goods_prices_offers_schema)
            return None
        self.create(suggested_goods_prices_offers_model=suggested_goods_prices_offers_model_)
        # self.populate_suggested_goods_prices_offers(schema_=suggested_goods_prices_offers_schema)
        return None
    

class DBSuggestedGoodsPricesBonusMerchantBonusUpdater:
    """
    Updater for offer mappings from Yandex Market
        """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_goods_prices_id(self, schema_: dict) -> int:
        """gets order_id"""
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == schema_.get('suggested_goods_id'))
        if suggested_goods_prices_queried.count() > 1:
            print(f"This thing {schema_.get('goods_id')} has duplicate ids in db")
        suggested_goods_prices_in_db = suggested_goods_prices_queried.first()
        if suggested_goods_prices_in_db:
            return suggested_goods_prices_in_db.id
        
    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPricesBonusMerchantBonus:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.__dict__ if not i.startswith('_')]

        suggested_goods_prices_bonus_merchant_bonus_schema = schema_
        suggested_goods_prices_bonus_merchant_bonus_schema['goods_prices_id'] = self.get_goods_prices_id(schema_=schema_)
        
        DBMerchantUpdater(
            client_session=self.sesh, db_session=self.db_session, db_engine=self.db_engine
        ).refresh(
            merchant_schema_={
                'id': suggested_goods_prices_bonus_merchant_bonus_schema['merchant_id'],
                'name': suggested_goods_prices_bonus_merchant_bonus_schema['merchant_name']
            }
        )

        suggested_goods_prices_bonus_merchant_bonus_schema = {
            key: value for key, value in suggested_goods_prices_bonus_merchant_bonus_schema.items() if key in req_fields
        }
        return sbermm_models.SuggestedGoodsPricesBonusMerchantBonus(
            **suggested_goods_prices_bonus_merchant_bonus_schema
        )
    
    def check_integrity(self, suggested_goods_prices_bonus_merchant_bonus_model: sbermm_models.SuggestedGoodsPricesBonusMerchantBonus) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_bonus_merchant_bonus_queried: sbermm_models.SuggestedGoodsPricesBonusMerchantBonus = self.db_session.query(
            sbermm_models.SuggestedGoodsPricesBonusMerchantBonus
        ).filter(
            sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.goods_prices_id == suggested_goods_prices_bonus_merchant_bonus_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.merchant_id == suggested_goods_prices_bonus_merchant_bonus_model.merchant_id
        )
        if suggested_goods_prices_bonus_merchant_bonus_queried.count() > 1:
            print(f"This suggested goods prices with id - {suggested_goods_prices_bonus_merchant_bonus_model.goods_prices_id} has duplicates")
        suggested_goods_prices_bonus_merchant_bonus_queried = suggested_goods_prices_bonus_merchant_bonus_queried.first()
        if suggested_goods_prices_bonus_merchant_bonus_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_bonus_merchant_bonus_model: sbermm_models.SuggestedGoodsPricesBonusMerchantBonus) -> None:
        """Updates Product entity"""
        suggested_goods_prices_bonus_merchant_bonus_in_db: sbermm_models.SuggestedGoodsPricesBonusMerchantBonus = self.db_session.query(sbermm_models.SuggestedGoodsPricesBonusMerchantBonus).filter(
            sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.goods_prices_id == suggested_goods_prices_bonus_merchant_bonus_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesBonusMerchantBonus.merchant_id == suggested_goods_prices_bonus_merchant_bonus_model.merchant_id
        ).first()
        
        suggested_goods_prices_bonus_merchant_bonus_in_db.bonus_date = suggested_goods_prices_bonus_merchant_bonus_model.bonus_date
        suggested_goods_prices_bonus_merchant_bonus_in_db.k = suggested_goods_prices_bonus_merchant_bonus_model.k
    
        self.db_session.commit()

    def create(self, suggested_goods_prices_bonus_merchant_bonus_model: sbermm_models.SuggestedGoodsPricesBonusMerchantBonus) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_bonus_merchant_bonus_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_bonus_merchant_bonus_schema: dict) -> None:
        suggested_goods_prices_bonus_merchant_bonus_model_ = self.prep_model(schema_=suggested_goods_prices_bonus_merchant_bonus_schema)
        if self.check_integrity(suggested_goods_prices_bonus_merchant_bonus_model=suggested_goods_prices_bonus_merchant_bonus_model_):
            self.update(suggested_goods_prices_bonus_merchant_bonus_model=suggested_goods_prices_bonus_merchant_bonus_model_)
            # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_bonus_merchant_bonus_schema)
            return None
        self.create(suggested_goods_prices_bonus_merchant_bonus_model=suggested_goods_prices_bonus_merchant_bonus_model_)
        # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_bonus_merchant_bonus_schema)
        return None
    

class DBSuggestedGoodsPricesPriceHistoryUpdater:
    """
    Updater for offer mappings from Yandex Market
        """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_goods_prices_id(self, schema_: dict) -> int:
        """gets order_id"""
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == schema_.get('suggested_goods_id'))
        if suggested_goods_prices_queried.count() > 1:
            print(f"This thing {schema_.get('goods_id')} has duplicate ids in db")
        suggested_goods_prices_in_db = suggested_goods_prices_queried.first()
        if suggested_goods_prices_in_db:
            return suggested_goods_prices_in_db.id
        
    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPricesPriceHistory:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesPriceHistory.__dict__ if not i.startswith('_')]

        suggested_goods_prices_price_history_schema = schema_
        suggested_goods_prices_price_history_schema['goods_prices_id'] = self.get_goods_prices_id(schema_=schema_)

        suggested_goods_prices_price_history_schema = {
            key: value for key, value in suggested_goods_prices_price_history_schema.items() if key in req_fields
        }
        return sbermm_models.SuggestedGoodsPricesPriceHistory(
            **suggested_goods_prices_price_history_schema
        )
    
    def check_integrity(self, suggested_goods_prices_price_history_model: sbermm_models.SuggestedGoodsPricesPriceHistory) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_price_history_queried: sbermm_models.SuggestedGoodsPricesPriceHistory = self.db_session.query(
            sbermm_models.SuggestedGoodsPricesPriceHistory
        ).filter(
            sbermm_models.SuggestedGoodsPricesPriceHistory.goods_prices_id == suggested_goods_prices_price_history_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesPriceHistory.point_id == suggested_goods_prices_price_history_model.point_id
        )
        if suggested_goods_prices_price_history_queried.count() > 1:
            print(f"This suggested goods prices with id - {suggested_goods_prices_price_history_model.goods_prices_id} has duplicates")
        suggested_goods_prices_price_history_queried = suggested_goods_prices_price_history_queried.first()
        if suggested_goods_prices_price_history_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_price_history_model: sbermm_models.SuggestedGoodsPricesPriceHistory) -> None:
        """Updates Product entity"""
        suggested_goods_prices_price_history_in_db: sbermm_models.SuggestedGoodsPricesPriceHistory = self.db_session.query(sbermm_models.SuggestedGoodsPricesPriceHistory).filter(
            sbermm_models.SuggestedGoodsPricesPriceHistory.goods_prices_id == suggested_goods_prices_price_history_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesPriceHistory.point_id == suggested_goods_prices_price_history_model.point_id
        ).first()
        
        suggested_goods_prices_price_history_in_db.point_name = suggested_goods_prices_price_history_model.point_name
        suggested_goods_prices_price_history_in_db.point_value = suggested_goods_prices_price_history_model.point_value
    
        self.db_session.commit()

    def create(self, suggested_goods_prices_price_history_model: sbermm_models.SuggestedGoodsPricesPriceHistory) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_price_history_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_price_history_schema: dict) -> None:
        suggested_goods_prices_price_history_model_ = self.prep_model(schema_=suggested_goods_prices_price_history_schema)
        if self.check_integrity(suggested_goods_prices_price_history_model=suggested_goods_prices_price_history_model_):
            self.update(suggested_goods_prices_price_history_model=suggested_goods_prices_price_history_model_)
            # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_price_history_schema)
            return None
        self.create(suggested_goods_prices_price_history_model=suggested_goods_prices_price_history_model_)
        # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_price_histry_schema)
        return None
    

class DBSuggestedGoodsPricesPriceAdjustmentsUpdater:
    """
    Updater for offer mappings from Yandex Market
        """
    def __init__(
            self, client_session: Session,
            db_session, db_engine
    ) -> None:
        self.db_session = db_session
        self.db_engine = db_engine
        self.sesh = client_session

    def get_goods_prices_id(self, schema_: dict) -> int:
        """gets order_id"""
        suggested_goods_prices_queried: sbermm_models.SuggestedGoodsPrices = self.db_session.query(sbermm_models.SuggestedGoodsPrices).filter(
            sbermm_models.SuggestedGoodsPrices.suggested_goods_id == schema_.get('suggested_goods_id'))
        if suggested_goods_prices_queried.count() > 1:
            print(f"This thing {schema_.get('goods_id')} has duplicate ids in db")
        suggested_goods_prices_in_db = suggested_goods_prices_queried.first()
        if suggested_goods_prices_in_db:
            return suggested_goods_prices_in_db.id
        
    def prep_model(self, schema_: dict) -> sbermm_models.SuggestedGoodsPricesPriceAdjustments:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.SuggestedGoodsPricesPriceAdjustments.__dict__ if not i.startswith('_')]

        suggested_goods_prices_price_adjustments_schema = schema_
        suggested_goods_prices_price_adjustments_schema['goods_prices_id'] = self.get_goods_prices_id(schema_=schema_)

        suggested_goods_prices_price_adjustments_schema = {
            key: value for key, value in suggested_goods_prices_price_adjustments_schema.items() if key in req_fields
        }
        return sbermm_models.SuggestedGoodsPricesPriceAdjustments(
            **suggested_goods_prices_price_adjustments_schema
        )
    
    def check_integrity(self, suggested_goods_prices_price_adjustments_model: sbermm_models.SuggestedGoodsPricesPriceAdjustments) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        suggested_goods_prices_price_adjustments_queried: sbermm_models.SuggestedGoodsPricesPriceAdjustments = self.db_session.query(
            sbermm_models.SuggestedGoodsPricesPriceAdjustments
        ).filter(
            sbermm_models.SuggestedGoodsPricesPriceAdjustments.goods_prices_id == suggested_goods_prices_price_adjustments_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesPriceAdjustments.type == suggested_goods_prices_price_adjustments_model.type
        )
        if suggested_goods_prices_price_adjustments_queried.count() > 1:
            print(f"This suggested goods prices with id - {suggested_goods_prices_price_adjustments_model.goods_prices_id} has duplicates")
        suggested_goods_prices_price_adjustments_queried = suggested_goods_prices_price_adjustments_queried.first()
        if suggested_goods_prices_price_adjustments_queried:
            return True
        return False
    
    def update(self, suggested_goods_prices_price_adjustments_model: sbermm_models.SuggestedGoodsPricesPriceAdjustments) -> None:
        """Updates Product entity"""
        suggested_goods_prices_price_adjustments_in_db: sbermm_models.SuggestedGoodsPricesPriceAdjustments = self.db_session.query(sbermm_models.SuggestedGoodsPricesPriceAdjustments).filter(
            sbermm_models.SuggestedGoodsPricesPriceAdjustments.goods_prices_id == suggested_goods_prices_price_adjustments_model.goods_prices_id,
            sbermm_models.SuggestedGoodsPricesPriceAdjustments.type == suggested_goods_prices_price_adjustments_model.type
        ).first()
        
        suggested_goods_prices_price_adjustments_in_db.amount = suggested_goods_prices_price_adjustments_model.amount
    
        self.db_session.commit()

    def create(self, suggested_goods_prices_price_adjustments_model: sbermm_models.SuggestedGoodsPricesPriceAdjustments) -> None:
        """Creates Order entity"""
        self.db_session.add(suggested_goods_prices_price_adjustments_model)
        self.db_session.commit()

    
    def refresh(self, suggested_goods_prices_price_adjustments_schema: dict) -> None:
        suggested_goods_prices_price_adjustments_model_ = self.prep_model(schema_=suggested_goods_prices_price_adjustments_schema)
        if self.check_integrity(suggested_goods_prices_price_adjustments_model=suggested_goods_prices_price_adjustments_model_):
            self.update(suggested_goods_prices_price_adjustments_model=suggested_goods_prices_price_adjustments_model_)
            # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_price_adjustments_schema)
            return None
        self.create(suggested_goods_prices_price_adjustments_model=suggested_goods_prices_price_adjustments_model_)
        # self.populate_suggested_goods_prices_bonus_merchant_bonus(schema_=suggested_goods_prices_price_adjustments_schema)
        return None