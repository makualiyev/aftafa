from sqlalchemy.exc import IntegrityError

from requests import Session

import aftafa.client.megamarket.models as sbermm_models


class DBMerchantGoodsOutletsUpdater:
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

    def prep_model(self, schema_: dict) -> sbermm_models.MerchantGoodsOutlets:
        """prepares ORM model for a given schema"""
        req_fields: list[str] = [i for i in sbermm_models.MerchantGoodsOutlets.__dict__ if not i.startswith('_')]

        merchant_goods_outlet_schema = schema_
        merchant_goods_outlet_schema = {key: value for key, value in merchant_goods_outlet_schema.items() if key in req_fields}
        if not merchant_goods_outlet_schema.get('instock'):
            merchant_goods_outlet_schema['instock'] = 0
        return sbermm_models.MerchantGoodsOutlets(**merchant_goods_outlet_schema)
    
    def check_integrity(self, merchant_goods_outlet_model: sbermm_models.MerchantGoodsOutlets) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        merchant_goods_outlet_queried: sbermm_models.MerchantGoodsOutlets = self.db_session.query(sbermm_models.MerchantGoodsOutlets).filter(
            sbermm_models.MerchantGoodsOutlets.outlet_id == int(merchant_goods_outlet_model.outlet_id),
            sbermm_models.MerchantGoodsOutlets.merchant_goods_id == merchant_goods_outlet_model.merchant_goods_id
        )
        if merchant_goods_outlet_queried.count() > 1:
            print(f"This order item with id - {merchant_goods_outlet_model.merchant_offer_id} for this price type ({merchant_goods_outlet_model.outlet_id}) has duplicates")
        merchant_goods_outlet_queried = merchant_goods_outlet_queried.first()
        if merchant_goods_outlet_queried:
            return True
        return False
    
    def update(self, merchant_goods_outlet_model: sbermm_models.MerchantGoodsOutlets) -> None:
        """Updates Product entity"""
        merchant_gooods_outlet_in_db: sbermm_models.MerchantGoodsOutlets = self.db_session.query(sbermm_models.MerchantGoodsOutlets).filter(
            sbermm_models.MerchantGoodsOutlets.outlet_id == int(merchant_goods_outlet_model.outlet_id),
            sbermm_models.MerchantGoodsOutlets.merchant_goods_id == merchant_goods_outlet_model.merchant_goods_id
        ).first()

        merchant_gooods_outlet_in_db.instock = merchant_goods_outlet_model.instock

        self.db_session.commit()

    def create(self, merchant_goods_outlet_model: sbermm_models.MerchantGoodsOutlets) -> None:
        """Creates Order entity"""
        self.db_session.add(merchant_goods_outlet_model)
        self.db_session.commit()

    
    def refresh(self, merchant_goods_outlet_schema: dict) -> None:
        merchant_goods_outlet_model_ = self.prep_model(schema_=merchant_goods_outlet_schema)
        if self.check_integrity(merchant_goods_outlet_model=merchant_goods_outlet_model_):
            self.update(merchant_goods_outlet_model=merchant_goods_outlet_model_)
            return None
        self.create(merchant_goods_outlet_model=merchant_goods_outlet_model_)
        return None
    