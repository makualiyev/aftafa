from datetime import datetime, date, timedelta
import time
from typing import Tuple, Generator, Union, Optional
from collections import Counter
from random import randint
from decimal import Decimal

from sqlalchemy import exc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import UUID4, ValidationError
from requests.models import Response
import pandas as pd


import aftafa.client.wildberries.models as wb_models
from aftafa.client.wildberries.models import session as db_session
import aftafa.client.wildberries.schemas as wb_schemas
from aftafa.client.wildberries.client import ClientSupplier, ClientSession, ClientMethod, ClientDirectSession
from aftafa.utils.helpers import bcolors


class DBCardUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's card"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id
    
    def process_card_from_list(self, card_list_entry: dict, flag: int = 0) -> None:
        """processes only nomenclature
        Parameters:

        flag : int = is set to 0 in a normal mode, but changes to 1 if
        there is nomenclature that is not present in card list from cursor
        method, usually some old cards
        """
        if flag == 1:
            chars: list[dict] = card_list_entry['characteristics']

            card_list_entry['brand'] = [dict_['Бренд'] for dict_ in chars if dict_.get('Бренд')][0]
            card_list_entry['object'] = [dict_['Предмет'] for dict_ in chars if dict_.get('Предмет')][0]
            card_list_entry['updateAt'] = None

        nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=card_list_entry['nmID']).first()
        if nomenclature_in_db:
            nomenclature_in_db.vendor_code = card_list_entry['vendorCode']
            nomenclature_in_db.brand = card_list_entry['brand']
            nomenclature_in_db.object = card_list_entry['object']
            nomenclature_in_db.updated_at = card_list_entry['updateAt']
            nomenclature_in_db.name = (
                ' '.join([
                    card_list_entry['object'],
                    card_list_entry['brand'],
                    card_list_entry['vendorCode']
                ])
            )
            nomenclature_in_db.primary_image = (card_list_entry['mediaFiles'][0] if card_list_entry['mediaFiles'] else None)

            try:
                assert nomenclature_in_db.supplier_id == self.supp_id, f"Variation is on wrong Nomenclature - {card_list_entry['nmID']}"
            except AssertionError as e:
                print('Assertion error', e)
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return None

        nomenclature_model: wb_models.Nomenclature = wb_models.Nomenclature(
            id=card_list_entry['nmID'],
            vendor_code=card_list_entry['vendorCode'],
            brand = card_list_entry['brand'],
            object = card_list_entry['object'],
            updated_at = card_list_entry['updateAt'],
            name = (
                ' '.join([
                    card_list_entry['object'],
                    card_list_entry['brand'],
                    card_list_entry['vendorCode']
                ])
            ),
            primary_image = (card_list_entry['mediaFiles'][0] if card_list_entry['mediaFiles'] else None),
            supplier_id=self.supp_id
        )
        db_session.add(nomenclature_model)
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)
        return None

    def process_card_from_filter(self, card_filter_entry: dict) -> None:
        """processes variations and configures card ids as FKs"""
        def process_imt_card(card_entry: dict) -> wb_models.Card:
            imt_card_in_db: wb_models.Card = db_session.query(wb_models.Card).filter_by(id=card_entry['imtID']).first()
            if imt_card_in_db:
                return None
            imt_card_model: wb_models.Card = wb_models.Card(id=card_entry['imtID'], supplier_id=self.supp_id, updated_at=datetime.today())
            try:
                db_session.add(imt_card_model)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
        
        def add_card_to_nm_relation(nm_id: int, imt_id: int, card_filter_entry_: dict) -> None:
            nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id).first()
            if not nomenclature_in_db:
                print(nm_id)
                self.process_card_from_list(card_list_entry=card_filter_entry_, flag=1)
                nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id).first()
            nomenclature_in_db.card_id = imt_id
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)

        def process_variations(variation_entry: dict) -> None:
            # vars: list[dict[str, Union[int, str, list[str]]]] = [var_ for var_ in variation_entry['sizes']]
            for var_ in variation_entry['sizes']:
                var_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter_by(id=var_['chrtID']).first()
                if var_in_db:
                    var_in_db.tech_size = var_['techSize']
                    var_in_db.wb_size = var_['wbSize']
                    var_in_db.barcode = (var_['skus'][0] if var_['skus'] else None)
                    var_in_db.alt_id = ''.join([
                        str(variation_entry['nmID']), var_['techSize']
                    ])
                    try:
                        assert var_in_db.nomenclature_id == variation_entry['nmID'], f"Variation is on wrong Nomenclature - {var_['chrtID']}"
                    except AssertionError as e:
                        print('Assertion error', e)
                    try:
                        db_session.commit()
                    except IntegrityError as e:
                        print(f"failed to commit ->", e)
                else:
                    var_model: wb_models.Variation = wb_models.Variation(
                        id=var_['chrtID'],
                        nomenclature_id=variation_entry['nmID'],
                        tech_size=var_['techSize'],
                        wb_size=var_['wbSize'],
                        barcode=(var_['skus'][0] if var_['skus'] else None),
                        alt_id=(''.join([
                                str(variation_entry['nmID']), var_['techSize']
                            ]))
                    )
                    db_session.add(var_model)
                    try:
                        db_session.commit()
                    except IntegrityError as e:
                        print(f"failed to commit ->", e)
        
        process_imt_card(card_entry=card_filter_entry)
        add_card_to_nm_relation(card_filter_entry['nmID'], imt_id=card_filter_entry['imtID'], card_filter_entry_=card_filter_entry)
        process_variations(variation_entry=card_filter_entry)


class DBV2CardUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's card"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id
    
    def process_card_from_list(self, card_list_entry: dict, flag: int = 0) -> None:
        """processes only nomenclature
        Parameters:

        flag : int = is set to 0 in a normal mode, but changes to 1 if
        there is nomenclature that is not present in card list from cursor
        method, usually some old cards
        """
        if flag == 1:
            chars: list[dict] = card_list_entry['characteristics']

            card_list_entry['brand'] = [dict_['Бренд'] for dict_ in chars if dict_.get('Бренд')][0]
            card_list_entry['object'] = [dict_['Предмет'] for dict_ in chars if dict_.get('Предмет')][0]
            card_list_entry['updatedAt'] = None

        nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=card_list_entry['nmID']).first()
        if nomenclature_in_db:
            nomenclature_in_db.vendor_code = card_list_entry['vendorCode']
            nomenclature_in_db.brand = card_list_entry['brand']
            nomenclature_in_db.object = card_list_entry['subjectName']
            nomenclature_in_db.updated_at = card_list_entry['updatedAt']
            nomenclature_in_db.name = (
                ' '.join([
                    card_list_entry['subjectName'],
                    card_list_entry['brand'],
                    card_list_entry['vendorCode']
                ])
            )
            nomenclature_in_db.primary_image = (card_list_entry['photos'][0]['big'] if card_list_entry.get('photos') else None)

            try:
                assert nomenclature_in_db.supplier_id == self.supp_id, f"Variation is on wrong Nomenclature - {card_list_entry['nmID']}"
            except AssertionError as e:
                print('Assertion error', e)
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return None

        nomenclature_model: wb_models.Nomenclature = wb_models.Nomenclature(
            id=card_list_entry['nmID'],
            vendor_code=card_list_entry['vendorCode'],
            brand = card_list_entry['brand'],
            object = card_list_entry['subjectName'],
            updated_at = card_list_entry['updatedAt'],
            name = (
                ' '.join([
                    card_list_entry['subjectName'],
                    card_list_entry['brand'],
                    card_list_entry['vendorCode']
                ])
            ),
            primary_image = (card_list_entry['photos'][0]['big'] if card_list_entry.get('photos') else None),
            supplier_id=self.supp_id
        )
        db_session.add(nomenclature_model)
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)
        return None

    def process_card_from_filter(self, card_filter_entry: dict) -> None:
        """processes variations and configures card ids as FKs"""
        def process_imt_card(card_entry: dict) -> wb_models.Card:
            imt_card_in_db: wb_models.Card = db_session.query(wb_models.Card).filter_by(id=card_entry['imtID']).first()
            if imt_card_in_db:
                return None
            imt_card_model: wb_models.Card = wb_models.Card(id=card_entry['imtID'], supplier_id=self.supp_id, updated_at=datetime.today())
            try:
                db_session.add(imt_card_model)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
        
        def add_card_to_nm_relation(nm_id: int, imt_id: int, card_filter_entry_: dict) -> None:
            nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id).first()
            if not nomenclature_in_db:
                print(nm_id)
                self.process_card_from_list(card_list_entry=card_filter_entry_, flag=1)
                nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id).first()
            nomenclature_in_db.card_id = imt_id
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)

        def process_variations(variation_entry: dict) -> None:
            # vars: list[dict[str, Union[int, str, list[str]]]] = [var_ for var_ in variation_entry['sizes']]
            for var_ in variation_entry['sizes']:
                var_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter_by(id=var_['chrtID']).first()
                if var_in_db:
                    var_in_db.tech_size = var_['techSize']
                    var_in_db.wb_size = var_['wbSize']
                    var_in_db.barcode = (var_['skus'][0] if var_['skus'] else None)
                    var_in_db.alt_id = ''.join([
                        str(variation_entry['nmID']), var_['techSize']
                    ])
                    try:
                        assert var_in_db.nomenclature_id == variation_entry['nmID'], f"Variation is on wrong Nomenclature - {var_['chrtID']}"
                    except AssertionError as e:
                        print('Assertion error', e)
                    try:
                        db_session.commit()
                    except IntegrityError as e:
                        print(f"failed to commit ->", e)
                else:
                    var_model: wb_models.Variation = wb_models.Variation(
                        id=var_['chrtID'],
                        nomenclature_id=variation_entry['nmID'],
                        tech_size=var_['techSize'],
                        wb_size=var_['wbSize'],
                        barcode=(var_['skus'][0] if var_['skus'] else None),
                        alt_id=(''.join([
                                str(variation_entry['nmID']), var_['techSize']
                            ]))
                    )
                    db_session.add(var_model)
                    try:
                        db_session.commit()
                    except IntegrityError as e:
                        print(f"failed to commit ->", e)
        
        process_imt_card(card_entry=card_filter_entry)
        add_card_to_nm_relation(card_filter_entry['nmID'], imt_id=card_filter_entry['imtID'], card_filter_entry_=card_filter_entry)
        process_variations(variation_entry=card_filter_entry)


class DBOrderUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's card"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def convert_decimals(self, price_: str) -> Decimal:
        return Decimal(price_[:-2] + '.' + price_[-2:])

    
    def prep_model(self, schema_: wb_schemas.GetOrdersOrder) -> wb_models.Order:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.Order.__dict__ if not i.startswith('_')]
        order_schema: dict[str, str] = schema_.dict(by_alias=False)

        order_schema['supplier_id'] = self.supp_id
        order_schema['nomenclature_id'] = order_schema['nm_id']
        order_schema['variation_id'] = order_schema['chrt_id']
        order_schema['vendor_code'] = order_schema['article']
        order_schema['barcode'] = order_schema['skus'][0]
        order_schema['price'] = self.convert_decimals(order_schema['price'])
        order_schema['converted_price'] = self.convert_decimals(order_schema['converted_price'])
        order_schema['currency_code'] = wb_schemas.CurrencyCodeEnum(order_schema['currency_code']).name
        order_schema['converted_currency_code'] = wb_schemas.CurrencyCodeEnum(order_schema['converted_currency_code']).name

        order_schema = {key: value for key, value in order_schema.items() if key in req_fields}
        return wb_models.Order(**order_schema)

    def check_integrity(self, order_model: wb_models.Order) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: wb_models.Order = self.db_session.query(wb_models.Order).filter(
            wb_models.Order.supplier_id == order_model.supplier_id,
            wb_models.Order.id == order_model.id
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, order_model: wb_models.Order) -> None:
        """Updates Product entity"""
        product_in_db: wb_models.Order = self.db_session.query(wb_models.Order).filter(
            wb_models.Order.supplier_id == order_model.supplier_id,
            wb_models.Order.id == order_model.id
        ).first()

        product_in_db.price = order_model.price
        # product_in_db.market_price = order_model.market_price
        # product_in_db.currency = order_model.currency
        # product_in_db.date_start = order_model.date_start
        # product_in_db.date_end = order_model.date_end
        
        # product_in_db.export_status = order_model.export_status
        # product_in_db.approval_status = order_model.approval_status
        # product_in_db.market_price_status = order_model.market_price_status

        self.db_session.commit()

        # try:
        #     assert int(product_in_db.price) == int(order_model.price), f"for this product {product_in_db.material_number} not the same prices"
        #     assert product_in_db.promo_price == order_model.promo_price, f"for this product {product_in_db.material_number} not the same promo prices"
        # except AssertionError as err:
        #     print(err)
        

    def create(self, order_model: wb_models.Order) -> None:
        """Creates Product entity"""
        self.db_session.add(order_model)
        self.db_session.commit()
            



class DBPriceUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's card"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    def process_entry(self, dict_entry: dict) -> None:
        """processes each entry of a price info"""
        nomenclature_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=dict_entry['nmId']).first()
        if not nomenclature_in_db:
            print(f"This nomenclature is missing in the DB, please take a look -> {dict_entry['nmId']}")
            return False
        price_info_in_db: wb_models.NomenclaturePrice = (
                    db_session
                            .query(wb_models.NomenclaturePrice)
                            .filter_by(nomenclature_id=nomenclature_in_db.id, updated_at=datetime.now().date())
                            .first()
        )
        if not price_info_in_db:
            price_info_to_add: wb_models.NomenclaturePrice = wb_models.NomenclaturePrice(
                nomenclature_id=nomenclature_in_db.id,
                price=dict_entry['price'],
                discount=dict_entry['discount'],
                promocode=dict_entry['promoCode'],
                updated_at=datetime.now().date()
            )
            db_session.add(price_info_to_add)
        else:
            price_info_in_db.price = dict_entry['price']
            price_info_in_db.discount = dict_entry['discount']
            price_info_in_db.promocode = dict_entry['promoCode']

        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)


class DBSupplyUpdater:
    """small class for warehouse updating"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def process_entry(self, dict_entry: dict) -> None:
        """updating supplies"""
        supply_in_db: wb_models.Supply = db_session.query(wb_models.Supply).filter_by(id=dict_entry['id']).first()
        if not supply_in_db:
            supply_in_db = wb_models.Supply(
                id=dict_entry['id'],
                supplier_id=self.supp_id,
                name=dict_entry['name'],
                created_at=dict_entry['createdAt'],
                closed_at=(dict_entry['closedAt'] if dict_entry['closedAt'] else None),
                scan_dt=(dict_entry['scanDt'] if dict_entry['scanDt'] else None),
                is_large_cargo=dict_entry['isLargeCargo'],
                done=dict_entry['done']
            )
            db_session.add(supply_in_db)
        else:
            supply_in_db.name = dict_entry['name']
            supply_in_db.closed_at = (dict_entry['closedAt'] if dict_entry['closedAt'] else None)
            supply_in_db.scan_dt = (dict_entry['scanDt'] if dict_entry['scanDt'] else None)
            supply_in_db.is_large_cargo = dict_entry['isLargeCargo']
            supply_in_db.done = dict_entry['done']
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)


class DBWarehouseUpdater:
    """small class for supplies updating"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    def process_entry(self, dict_entry: dict) -> None:
        """updating warehouses"""
        wh_in_db: wb_models.Warehouse = db_session.query(wb_models.Warehouse).filter_by(id=dict_entry['id']).first()
        supp_id: int = db_session.query(wb_models.Supplier).filter_by(name=self.sesh.supplier.name).first().id
        if not wh_in_db:
            wh_to_add = wb_models.Warehouse(id=dict_entry['id'], name=dict_entry['name'], supplier_id=supp_id, is_active=True)
            db_session.add(wh_to_add)
        else:
            wh_in_db.name = dict_entry['name']
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)



class DBStockUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's stocks (supply stocks)"""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    def process_entry(self, dict_entry: dict) -> None:
        """processes each entry"""
        def check_warehouse(dict_entry: dict) -> None:
            """check whether a warehouse is in the DB and if not, adds it"""
            wh_in_db: wb_models.SupplyWarehouse = db_session.query(wb_models.SupplyWarehouse).filter_by(
                                                    id=dict_entry['warehouse']).first()
            if not wh_in_db:
                wh_to_add: wb_models.SupplyWarehouse = wb_models.SupplyWarehouse(
                                                                id=dict_entry['warehouse'],
                                                                name=dict_entry['warehouseName']
                                                            )
                db_session.add(wh_to_add)
                try:
                    db_session.commit()
                except IntegrityError as e:
                    print(f"failed to commit ->", e)
                return True
            try:
                assert wh_in_db.name == dict_entry['warehouseName']
            except AssertionError as e:
                print(f"This warehouse has different representation in the DB and from API -> {dict_entry['warehouseName']} -- {wh_in_db.name}", e)
            return True


        stock_in_db: wb_models.SupplyStock = db_session.query(wb_models.SupplyStock).filter_by(
                                                    nomenclature_id=dict_entry['nmId'],
                                                    warehouse_id=dict_entry['warehouse'],
                                                    sc_code=dict_entry['SCCode'],
                                                    last_change_date=dict_entry['lastChangeDate']
                                                ).first()
        nm_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=dict_entry['nmId']).first()

        if not nm_in_db:
            print(f"This nomenclature is missing from the WB -> {dict_entry['nmId']}")
            return False

        check_warehouse(dict_entry=dict_entry)
        if not stock_in_db:
            stock_to_add: wb_models.SupplyStock = wb_models.SupplyStock(
                nomenclature_id=dict_entry['nmId'],
                supplier_article=dict_entry['supplierArticle'],
                tech_size=dict_entry['techSize'],
                barcode=dict_entry['barcode'],
                is_supply=dict_entry['isSupply'],
                is_realization=dict_entry['isRealization'],
                warehouse_id=dict_entry['warehouse'],
                warehouse=dict_entry['warehouseName'],
                quantity=dict_entry['quantity'],
                qunatity_full=dict_entry['quantityFull'],
                qunatity_not_in_orders=dict_entry['quantityNotInOrders'],
                in_way_to_client=dict_entry['inWayToClient'],
                in_way_from_client=dict_entry['inWayFromClient'],
                days_on_site=dict_entry['daysOnSite'],
                brand=dict_entry['brand'],
                sc_code=dict_entry['SCCode'],
                last_change_date=dict_entry['lastChangeDate']
            )
            db_session.add(stock_to_add)
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return True
        
        # updating...
        stock_in_db.supplier_article = dict_entry['supplierArticle']
        stock_in_db.tech_size = dict_entry['techSize']
        stock_in_db.barcode = dict_entry['barcode']
        stock_in_db.is_supply = dict_entry['isSupply']
        stock_in_db.is_realization = dict_entry['isRealization']
        stock_in_db.warehouse = dict_entry['warehouseName']
        stock_in_db.quantity = dict_entry['quantity']
        stock_in_db.qunatity_full = dict_entry['quantityFull']
        stock_in_db.qunatity_not_in_orders = dict_entry['quantityNotInOrders']
        stock_in_db.in_way_to_client = dict_entry['inWayToClient']
        stock_in_db.in_way_from_client = dict_entry['inWayFromClient']
        stock_in_db.days_on_site = dict_entry['daysOnSite']
        stock_in_db.brand = dict_entry['brand']
        stock_in_db.sc_code = dict_entry['SCCode']
        stock_in_db.last_change_date = dict_entry['lastChangeDate']
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)
        return True


class DBBackSupplyStockUpdater:
    """experimenting with classes that updates info in the DB
    regarding a product's stocks (supply stocks)"""
    def __init__(self, client_session: ClientDirectSession) -> None:
        self.sesh = client_session

    def process_wh_list(self, warehouse_dict: dict[str, str]) -> dict[str, dict[str, Union[str, int]]]:
        """
        checks each warehouse in a warehouse list
        """
        wh_by_name = lambda name: (db_session.query(
                                wb_models.SupplyWarehouse
                            ).filter(
                                wb_models.SupplyWarehouse.name == name
                            ).first())

        refreshed_wh_list: dict[str, dict[str, Union[str, int]]] = {}
        for wh_key, wh_name in warehouse_dict.items():
            wh_in_db: wb_models.SupplyWarehouse = wh_by_name(name=wh_name)
            if wh_in_db:
                refreshed_wh_list[wh_key] = {
                    'wh_id': wh_in_db.id,
                    'wh_name': wh_in_db.name
                }
                continue
            wh_to_add: wb_models.SupplyWarehouse = wb_models.SupplyWarehouse(
                                id=randint(100, 900),
                                name=wh_name
                            )
            db_session.add(wh_to_add)
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            wh_in_db: wb_models.SupplyWarehouse = wh_by_name(name=wh_name)
            refreshed_wh_list[wh_key] = {
                'wh_id': wh_in_db.id,
                'wh_name': wh_in_db.name
            }
        return refreshed_wh_list
    
    def check_variation(self, alt_id: str) -> Union[int, bool]:
        """
        checks whether variation is in the db or not
        """
        variation_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter(
            wb_models.Variation.alt_id == alt_id
        ).first()
        if not variation_in_db:
            print(
                bcolors.FAIL,
                f'Unfortunately this alt id of variation is not present in the DB -> {alt_id}',
                bcolors.ENDC
            )
            return False
        return variation_in_db.id


    def process_entry(self, balances_entry: dict, wh_list: dict) -> None:
        """processes each entry"""
        alt_id: str = (str(balances_entry['nmId']) + str(balances_entry['techSize']))
        var_id = self.check_variation(alt_id=alt_id)
        if not var_id:
            return False

        wh_to_check: list = []
        for wh_key in wh_list.keys():
            if balances_entry[wh_key]:
                wh_to_check.append(wh_key)

        
        for key in wh_to_check:
            stock_in_db: wb_models.BackSupplyStock = db_session.query(wb_models.BackSupplyStock).filter(
                wb_models.BackSupplyStock.variation_id == var_id,
                wb_models.BackSupplyStock.nomenclature_id == balances_entry['nmId'],
                wb_models.BackSupplyStock.updated_at == datetime.today().date(),
                wb_models.BackSupplyStock.warehouse == wh_list[key]['wh_name'],
                wb_models.BackSupplyStock.warehouse_id == wh_list[key]['wh_id']
            )
            if stock_in_db.count() > 1:
                print(
                    bcolors.WARNING,
                    f"Something's wrong with this stock entry (var_id, date, warehouse_id) -> \
                        ({var_id}, {datetime.today().date()}, {wh_list[key]['wh_id']})",
                    bcolors.ENDC
                )
                continue
            if stock_in_db.first():
                stock_in_db.quantity_for_sale = balances_entry[key]
                wh_list[key]['check'] = 1           # FIXME: if 1 then it is skipped then
                try:
                    db_session.commit()
                except IntegrityError as e:
                    print(f"failed to commit ->", e)
                continue
            wh_list[key]['check'] = 0
            
                
        
        model_base: wb_models.BackSupplyStock = lambda entry, var_id_:  (wb_models.BackSupplyStock(
                    nomenclature_id=entry['nmId'],
                    variation_id=var_id_,
                    barcode=entry.get('barcode', ''),
                    supplier_article=entry['supplierArticle']
                ))

        for wh_key in wh_list.keys():
            if balances_entry[wh_key]:
                if wh_list[wh_key]['check']:
                    continue
                model_base_ = model_base(entry=balances_entry, var_id_=var_id)
                model_base_.warehouse = wh_list[wh_key]['wh_name']
                model_base_.warehouse_id = wh_list[wh_key]['wh_id']
                model_base_.quantity_for_sale = balances_entry[wh_key]
                
                db_session.add(model_base_)
                try:
                    db_session.commit()
                except IntegrityError as e:
                    print(f"failed to commit ->", e)

        balances_check: dict[str, int] = [
            balances_entry.get('quantityInTransit', 0),
            balances_entry.get('quantityInTransitFromClient', 0),
            balances_entry.get('quantityInTransitToClient', 0)
        ]
        balances_sum: int = sum(map(lambda x: 0 if isinstance(x, type(None)) else x, balances_check))

        if balances_sum > 0:
            transit_in_db: wb_models.BackSupplyStock = db_session.query(wb_models.BackSupplyStock).filter(
                wb_models.BackSupplyStock.variation_id == var_id,
                wb_models.BackSupplyStock.nomenclature_id == balances_entry['nmId'],
                wb_models.BackSupplyStock.updated_at == datetime.today().date(),
                wb_models.BackSupplyStock.warehouse == 'Транзит',
                wb_models.BackSupplyStock.warehouse_id == 666
            ).first()
            if not transit_in_db:
                transit_model = model_base(entry=balances_entry, var_id_=var_id)
                transit_model.warehouse = 'Транзит'
                transit_model.warehouse_id = 666
                transit_model.quantity_in_transit = balances_sum

                db_session.add(transit_model)
                try:
                    db_session.commit()
                except IntegrityError as e:
                    print(f"failed to commit ->", e)
                return True
            
            transit_in_db.quantity_in_transit = balances_sum
            try:
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return True


        


        # stock_in_db: wb_models.SupplyStock = db_session.query(wb_models.SupplyStock).filter_by(
        #                                             nomenclature_id=dict_entry['nmId'],
        #                                             warehouse_id=dict_entry['warehouse'],
        #                                             sc_code=dict_entry['SCCode'],
        #                                             last_change_date=dict_entry['lastChangeDate']
        #                                         ).first()
        # nm_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=dict_entry['nmId']).first()

        # if not nm_in_db:
        #     print(f"This nomenclature is missing from the WB -> {dict_entry['nmId']}")
        #     return False

        # check_warehouse(dict_entry=dict_entry)
        # if not stock_in_db:
        #     stock_to_add: wb_models.SupplyStock = wb_models.SupplyStock(
        #         nomenclature_id=dict_entry['nmId'],
        #         supplier_article=dict_entry['supplierArticle'],
        #         tech_size=dict_entry['techSize'],
        #         barcode=dict_entry['barcode'],
        #         is_supply=dict_entry['isSupply'],
        #         is_realization=dict_entry['isRealization'],
        #         warehouse_id=dict_entry['warehouse'],
        #         warehouse=dict_entry['warehouseName'],
        #         quantity=dict_entry['quantity'],
        #         qunatity_full=dict_entry['quantityFull'],
        #         qunatity_not_in_orders=dict_entry['quantityNotInOrders'],
        #         in_way_to_client=dict_entry['inWayToClient'],
        #         in_way_from_client=dict_entry['inWayFromClient'],
        #         days_on_site=dict_entry['daysOnSite'],
        #         brand=dict_entry['brand'],
        #         sc_code=dict_entry['SCCode'],
        #         last_change_date=dict_entry['lastChangeDate']
        #     )
        #     db_session.add(stock_to_add)
        #     try:
        #         db_session.commit()
        #     except IntegrityError as e:
        #         print(f"failed to commit ->", e)
        #     return True
        
        # # updating...
        # stock_in_db.supplier_article = dict_entry['supplierArticle']
        # stock_in_db.tech_size = dict_entry['techSize']
        # stock_in_db.barcode = dict_entry['barcode']
        # stock_in_db.is_supply = dict_entry['isSupply']
        # stock_in_db.is_realization = dict_entry['isRealization']
        # stock_in_db.warehouse = dict_entry['warehouseName']
        # stock_in_db.quantity = dict_entry['quantity']
        # stock_in_db.qunatity_full = dict_entry['quantityFull']
        # stock_in_db.qunatity_not_in_orders = dict_entry['quantityNotInOrders']
        # stock_in_db.in_way_to_client = dict_entry['inWayToClient']
        # stock_in_db.in_way_from_client = dict_entry['inWayFromClient']
        # stock_in_db.days_on_site = dict_entry['daysOnSite']
        # stock_in_db.brand = dict_entry['brand']
        # stock_in_db.sc_code = dict_entry['SCCode']
        # stock_in_db.last_change_date = dict_entry['lastChangeDate']
        # try:
        #     db_session.commit()
        # except IntegrityError as e:
        #     print(f"failed to commit ->", e)
        # return True


class DBSupplyOrderUpdater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        

    def process_order(self, od_dict_entry: dict) -> None:
        """processes just an order itself, without its positions yet"""
        # getting supplier id
        supp_id: int = db_session.query(wb_models.Supplier).filter_by(name=self.sesh.supplier.name).first().id
        order_in_db: wb_models.SupplyOrder = db_session.query(wb_models.SupplyOrder).filter_by(id=od_dict_entry['gNumber']).first()
        if not order_in_db:
            order_to_add: wb_models.SupplyOrder = wb_models.SupplyOrder(
                id=od_dict_entry['gNumber'],
                supplier_id=supp_id,
                order_date=od_dict_entry['date']
            )
            try:
                db_session.add(order_to_add)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return True
        order_in_db.order_date = od_dict_entry['date']
        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)
        return True

    def process_order_position(self, pos_dict_entry: dict) -> None:
        """processes just an order itself, without its positions yet"""
        def check_warehouse(wh_name: str) -> int:
            """checks warehouse in the DB, and if not present adds it to it.
            Returns warehouse's ID"""
            wh_in_db: wb_models.SupplyWarehouse = db_session.query(wb_models.SupplyWarehouse).filter_by(name=wh_name)
            if wh_in_db.first():
                if wh_in_db.count() > 1:
                    print(f"This warehouse has duplicates in the DB, - > {wh_name}")
                return wh_in_db.first().id
            return None
        
        def check_variation(var_id_: str, nm_id_: int) -> Union[int, bool]:
            """
            checks whether a variation is in the DB through wb_id (alt_id in db)
            """
            var_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter_by(alt_id=var_id_).first()
            var_nm_in_db: list[wb_models.Variation] = db_session.query(wb_models.Variation).filter_by(nomenclature_id=nm_id_).all()
            if not var_in_db:
                if len(var_nm_in_db) == 1:
                    return var_nm_in_db[0].id
                elif len(var_nm_in_db) > 1:
                    print(bcolors.FAIL, f"This variation hasn been found, but it has too many options check it -> nm_id: \
                        {pos_dict_entry['nmId']} - tech_size: {pos_dict_entry['techSize']}", bcolors.ENDC)
                    return 0
                else:
                    print(bcolors.FAIL, f"This variation hasn't been found, check it -> nm_id: {pos_dict_entry['nmId']} \
                    - tech_size: {pos_dict_entry['techSize']}", bcolors.ENDC)
                    return 0
            return var_in_db.id

        def check_nomenclature(nm_id_: int) -> bool:
            """checks whether a nomenclature is in the new base API, if not, just skips it"""
            nm_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id_).first()
            if not nm_in_db:
                print(f"This nomenclature is missing from the WB -> {nm_id_}")
                return False
            return True

        order_pos_in_db: wb_models.SupplyOrderPosition = db_session.query(wb_models.SupplyOrderPosition).filter_by(
                                                                    id=pos_dict_entry['odid']                                  # FIXME: it was query by two parameters
                                                                                                                                # id and order_id, but it'd changed to id only!
                                                                )
        if order_pos_in_db.count() > 1:
            print(bcolors.FAIL, f"This order has duplicates, check it -> \n new order id: {pos_dict_entry['gNumber']} \t order position id {pos_dict_entry['odid']} \
                                            \t old order id: {order_pos_in_db.order_id} ", bcolors.ENDC)
        if not check_nomenclature(nm_id_=pos_dict_entry['nmId']):
            return False
        var_id: int = check_variation(var_id_=(str(pos_dict_entry['nmId']) + pos_dict_entry['techSize']), nm_id_=pos_dict_entry['nmId'])

        if not order_pos_in_db.first():
            # add order position
            position_to_add: wb_models.SupplyOrderPosition = wb_models.SupplyOrderPosition(
                id=pos_dict_entry['odid'],
                order_id=pos_dict_entry['gNumber'],
                nomenclature_id=pos_dict_entry['nmId'],
                variation_id=(var_id if var_id else None),
                srid=(pos_dict_entry['srid'] if pos_dict_entry['srid'] != '' else None),
                supplier_article=pos_dict_entry['supplierArticle'],
                tech_size=pos_dict_entry['techSize'],
                barcode=pos_dict_entry['barcode'],
                warehouse_id=(check_warehouse(wh_name=pos_dict_entry['warehouseName'])),
                warehouse=pos_dict_entry['warehouseName'],
                region=pos_dict_entry['oblast'],
                total_price=pos_dict_entry['totalPrice'],
                discount_percent=pos_dict_entry['discountPercent'],
                is_cancel=pos_dict_entry['isCancel'],
                cancel_date=(pos_dict_entry['cancel_dt'] if pos_dict_entry['cancel_dt'] != '0001-01-01T00:00:00' else None),
                sticker=(pos_dict_entry['sticker'] if pos_dict_entry['sticker'] != '' else None),
                income_id=(pos_dict_entry['incomeID'] if pos_dict_entry['incomeID'] != 0 else None),
                last_change_date=pos_dict_entry['lastChangeDate']
            )
            try:
                db_session.add(position_to_add)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return True
        try:
            assert order_pos_in_db.first().nomenclature_id == pos_dict_entry['nmId']
        except AssertionError as e:
                print(f"This warehouse has different representation in the DB and from API -> {pos_dict_entry['nmId']} -- {order_pos_in_db.first().nomenclature_id}", e)
        
        order_pos_in_db.first().supplier_article = pos_dict_entry['supplierArticle']
        order_pos_in_db.first().tech_size = pos_dict_entry['techSize']
        order_pos_in_db.first().barcode = pos_dict_entry['barcode']
        order_pos_in_db.first().warehouse_id  = (check_warehouse(wh_name=pos_dict_entry['warehouseName']))
        order_pos_in_db.first().warehouse = pos_dict_entry['warehouseName']
        order_pos_in_db.first().region = pos_dict_entry['oblast']
        if order_pos_in_db.first().id == '9000662707996':
            print(bcolors.WARNING + f"CHECK here is total price - {pos_dict_entry['discountPercent']} and discount {pos_dict_entry['totalPrice']}" + bcolors.ENDC)
        order_pos_in_db.first().total_price = pos_dict_entry['totalPrice']
        order_pos_in_db.first().discount_percent = pos_dict_entry['discountPercent']
        order_pos_in_db.first().is_cancel = pos_dict_entry['isCancel']
        order_pos_in_db.first().cancel_date = (pos_dict_entry['cancel_dt'] if pos_dict_entry['cancel_dt'] != '0001-01-01T00:00:00' else None)
        order_pos_in_db.first().sticker = (pos_dict_entry['sticker'] if pos_dict_entry['sticker'] != '' else None)
        order_pos_in_db.first().income_id = (pos_dict_entry['incomeID'] if pos_dict_entry['incomeID'] != 0 else None)
        order_pos_in_db.first().last_change_date = pos_dict_entry['lastChangeDate']
        order_pos_in_db.first().srid = (pos_dict_entry['srid'] if pos_dict_entry['srid'] != '' else None)
        order_pos_in_db.first().variation_id = (var_id if var_id else None)

        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)

            

    def process_entry(self, dict_entry: dict) -> None:
        """processes each entry"""
        self.process_order(od_dict_entry=dict_entry)
        self.process_order_position(pos_dict_entry=dict_entry)


class DBSupplyOrderV2Updater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def prep_model(self, schema_: wb_schemas.SupplierOrdersV2) -> wb_models.SupplyOrderV2 | None:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.SupplyOrderV2.__dict__ if not i.startswith('_')]
        order_v2_schema: dict[str, str] = schema_.dict(by_alias=False)

        if order_v2_schema['nm_id'] and order_v2_schema['tech_size']:
            var_id_in_db: Optional[wb_models.Variation] = self.db_session.query(wb_models.Variation).filter(
                wb_models.Variation.alt_id == (str(order_v2_schema['nm_id']) + order_v2_schema['tech_size'])
            ).first()
        else:
            var_id_in_db: Optional[wb_models.Variation] = None
        if order_v2_schema['nm_id']:
            nm_in_db: Optional[wb_models.Nomenclature] = self.db_session.query(wb_models.Nomenclature).filter(
                wb_models.Nomenclature.id == order_v2_schema['nm_id']
            ).first()
            if not nm_in_db:
                order_v2_schema['nm_id'] = None

        if (not var_id_in_db) or (not order_v2_schema['nm_id']):
            unrecognized_prod_repr: str = f"""
                        supplier_article={order_v2_schema['supplier_article']},
                        brand={order_v2_schema['brand']},
                        category={order_v2_schema['category']},
                        subject={order_v2_schema['subject']},
                        barcode={order_v2_schema['barcode']}"""
            print(
                f"There is unrecognized product -> {unrecognized_prod_repr}"
            )
            return None

        order_v2_schema['supplier_id'] = self.supp_id
        order_v2_schema['nomenclature_id'] = order_v2_schema['nm_id']
        # order_v2_schema['id'] = order_v2_schema['rrd_id']
        order_v2_schema['variation_id'] = (var_id_in_db.id if var_id_in_db else var_id_in_db)

        order_v2_schema = {key: value for key, value in order_v2_schema.items() if key in req_fields}
        return wb_models.SupplyOrderV2(**order_v2_schema)

    def check_integrity(self, order_v2_model: wb_models.SupplyOrderV2) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        order_v2_in_db: wb_models.SupplyOrderV2 = self.db_session.query(wb_models.SupplyOrderV2).filter(
            wb_models.SupplyOrderV2.supplier_id == order_v2_model.supplier_id,
            wb_models.SupplyOrderV2.srid == order_v2_model.srid
        ).first()
        if order_v2_in_db:
            return True
        return False

    def update(self, order_v2_model: wb_models.SupplyOrderV2) -> None:
        """Updates Product entity"""
        order_v2_model: wb_models.SupplyOrderV2 = self.db_session.query(wb_models.SupplyOrderV2).filter(
            wb_models.SupplyOrderV2.supplier_id == order_v2_model.supplier_id,
            wb_models.SupplyOrderV2.srid == order_v2_model.srid
        ).first()

        order_v2_model.barcode = order_v2_model.barcode

        self.db_session.commit()
        

    def create(self, order_v2_model: wb_models.SupplyOrderV2) -> None:
        """Creates Product entity"""
        self.db_session.add(order_v2_model)
        self.db_session.commit()


class DBSupplySaleV2Updater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def prep_model(self, schema_: wb_schemas.SupplierSales) -> wb_models.SupplySaleV2:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.SupplySaleV2.__dict__ if not i.startswith('_')]
        sale_v2_schema: dict[str, str] = schema_.dict(by_alias=False)

        if sale_v2_schema['nm_id'] and sale_v2_schema['tech_size']:
            var_id_in_db: Optional[wb_models.Variation] = self.db_session.query(wb_models.Variation).filter(
                wb_models.Variation.alt_id == (str(sale_v2_schema['nm_id']) + sale_v2_schema['tech_size'])
            ).first()
        else:
            var_id_in_db: Optional[wb_models.Variation] = None
        if sale_v2_schema['nm_id']:
            nm_in_db: Optional[wb_models.Nomenclature] = self.db_session.query(wb_models.Nomenclature).filter(
                wb_models.Nomenclature.id == sale_v2_schema['nm_id']
            ).first()
            if not nm_in_db:
                sale_v2_schema['nm_id'] = None

        sale_v2_schema['supplier_id'] = self.supp_id
        sale_v2_schema['nomenclature_id'] = sale_v2_schema['nm_id']
        # sale_v2_schema['id'] = sale_v2_schema['rrd_id']
        sale_v2_schema['variation_id'] = (var_id_in_db.id if var_id_in_db else var_id_in_db)

        sale_v2_schema = {key: value for key, value in sale_v2_schema.items() if key in req_fields}
        return wb_models.SupplySaleV2(**sale_v2_schema)

    def check_integrity(self, sale_v2_model: wb_models.SupplySaleV2) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        sale_v2_in_db: wb_models.SupplySaleV2 = self.db_session.query(wb_models.SupplySaleV2).filter(
            wb_models.SupplySaleV2.supplier_id == sale_v2_model.supplier_id,
            wb_models.SupplySaleV2.sale_ID == sale_v2_model.sale_ID
        ).first()
        if sale_v2_in_db:
            return True
        return False

    def update(self, sale_v2_model: wb_models.SupplySaleV2) -> None:
        """Updates Product entity"""
        sale_v2_model: wb_models.SupplySaleV2 = self.db_session.query(wb_models.SupplySaleV2).filter(
            wb_models.SupplySaleV2.supplier_id == sale_v2_model.supplier_id,
            wb_models.SupplySaleV2.sale_ID == sale_v2_model.sale_ID
        ).first()

        sale_v2_model.barcode = sale_v2_model.barcode

        self.db_session.commit()
        

    def create(self, sale_v2_model: wb_models.SupplySaleV2) -> None:
        """Creates Product entity"""
        self.db_session.add(sale_v2_model)
        self.db_session.commit()


class DBSupplyStockV2Updater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession, extraction_ts: datetime) -> None:
        self.sesh = client_session
        self.db_session = db_session
        self.extraction_ts = extraction_ts

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def prep_model(self, schema_: wb_schemas.SupplierStocks) -> wb_models.SupplyStockV2:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.SupplyStockV2.__dict__ if not i.startswith('_')]
        stock_v2_schema: dict[str, str] = schema_.dict(by_alias=False)

        if stock_v2_schema['nm_id'] and stock_v2_schema['tech_size']:
            var_id_in_db: Optional[wb_models.Variation] = self.db_session.query(wb_models.Variation).filter(
                wb_models.Variation.alt_id == (str(stock_v2_schema['nm_id']) + stock_v2_schema['tech_size'])
            ).first()
        else:
            var_id_in_db: Optional[wb_models.Variation] = None
        if stock_v2_schema['nm_id']:
            nm_in_db: Optional[wb_models.Nomenclature] = self.db_session.query(wb_models.Nomenclature).filter(
                wb_models.Nomenclature.id == stock_v2_schema['nm_id']
            ).first()
            if not nm_in_db:
                stock_v2_schema['nm_id'] = None

        stock_v2_schema['supplier_id'] = self.supp_id
        stock_v2_schema['nomenclature_id'] = stock_v2_schema['nm_id']
        # stock_v2_schema['id'] = stock_v2_schema['rrd_id']
        stock_v2_schema['variation_id'] = (var_id_in_db.id if var_id_in_db else var_id_in_db)
        stock_v2_schema['extracted_at'] = self.extraction_ts

        stock_v2_schema = {key: value for key, value in stock_v2_schema.items() if key in req_fields}
        return wb_models.SupplyStockV2(**stock_v2_schema)

    def check_integrity(self, stock_v2_model: wb_models.SupplyStockV2) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        stock_v2_in_db: wb_models.SupplyStockV2 = self.db_session.query(wb_models.SupplyStockV2).filter(
            wb_models.SupplyStockV2.supplier_id == stock_v2_model.supplier_id,
            wb_models.SupplyStockV2.variation_id == stock_v2_model.variation_id,
            wb_models.SupplyStockV2.warehouse_name == stock_v2_model.warehouse_name,
            wb_models.SupplyStockV2.sc_code == stock_v2_model.sc_code
        ).first()
        if stock_v2_in_db:
            return True
        return False

    def update(self, stock_v2_model: wb_models.SupplyStockV2) -> None:
        """Updates Product entity"""
        stock_v2_model: wb_models.SupplyStockV2 = self.db_session.query(wb_models.SupplyStockV2).filter(
            wb_models.SupplyStockV2.supplier_id == stock_v2_model.supplier_id,
            wb_models.SupplyStockV2.variation_id == stock_v2_model.variation_id,
            wb_models.SupplyStockV2.warehouse_name == stock_v2_model.warehouse_name,
            wb_models.SupplyStockV2.sc_code == stock_v2_model.sc_code
        ).first()

        stock_v2_model.barcode = stock_v2_model.barcode

        self.db_session.commit()
        

    def create(self, stock_v2_model: wb_models.SupplyStockV2) -> None:
        """Creates Product entity"""
        self.db_session.add(stock_v2_model)
        self.db_session.commit()


class DBSupplySaleUpdater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    def check_warehouse(self, wh_name: dict) -> None:
            """check whether a warehouse is in the DB and if not, adds it"""
            wh_in_db: wb_models.SupplyWarehouse = db_session.query(wb_models.SupplyWarehouse).filter_by(
                                                    name=wh_name).first()
            if not wh_in_db:
                return None
            return wh_in_db.id
    
    def check_variation(self, var_id_: str, nm_id_: int, tech_size_: str) -> Union[int, bool]:
            """
            checks whether a variation is in the DB through wb_id (alt_id in db)
            """
            var_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter_by(alt_id=var_id_).first()
            var_nm_in_db: list[wb_models.Variation] = db_session.query(wb_models.Variation).filter_by(nomenclature_id=nm_id_).all()
            if not var_in_db:
                if len(var_nm_in_db) == 1:
                    return var_nm_in_db[0].id
                elif len(var_nm_in_db) > 1:
                    print(bcolors.FAIL, f"This variation hasn been found, but it has too many options check it -> nm_id: \
                        {nm_id_} - tech_size: {tech_size_}", bcolors.ENDC)
                    return 0
                else:
                    print(bcolors.FAIL, f"This variation hasn't been found, check it -> nm_id: {nm_id_} \
                    - tech_size: {tech_size_}", bcolors.ENDC)
                    return 0
            return var_in_db.id

    def check_order_position(self, order_pos_id_: int, g_number: str, srid_: Optional[str]) -> Union[int, tuple[int, str]]:
        """checks whether order position is presented in the DB"""
        order_pos_in_db: wb_models.SupplyOrderPosition = db_session.query(wb_models.SupplyOrderPosition).filter_by(
            id=order_pos_id_,
            order_id=g_number
        ).first()

        order_pos_by_srid_in_db : wb_models.SupplyOrderPosition = db_session.query(wb_models.SupplyOrderPosition).filter_by(
            srid=srid_
        ).first()

        if order_pos_in_db:
            return (g_number, order_pos_id_)
        elif order_pos_by_srid_in_db:               #FIXME : need to add method to fetch odid from srid
            
            print(bcolors.OKCYAN + f'Found this order position by srid! - \n order_position \t g_number \t srid \
                \n {order_pos_id_} \t {g_number} \t {srid_}' + bcolors.ENDC)

            return (order_pos_by_srid_in_db.order_id, order_pos_by_srid_in_db.id)
        else:
            print(f"Couldn't find this order position with gNumber {g_number} odid {order_pos_id_}")
            return -1


    def add_new_sale(self, sl_dict_entry: dict) -> wb_models.SupplySale | bool:
        """adds brand new sale entry into db"""
        
        order_info: Union[int, tuple[str, int]] = self.check_order_position(order_pos_id_=sl_dict_entry['odid'], g_number=sl_dict_entry['gNumber'], srid_=sl_dict_entry['srid'])
        if order_info == -1:
            return False

        var_id: int = self.check_variation(
            var_id_=''.join([str(sl_dict_entry['nmId']), sl_dict_entry['techSize']]),
            nm_id_=sl_dict_entry['nmId'],
            tech_size_=sl_dict_entry['techSize']
        )
        # order_position_: int = self.check_order_position(
        #     order_pos_id_=sl_dict_entry['odid'], g_number=sl_dict_entry['gNumber'], srid_=sl_dict_entry['srid']
        # )
        sale_model: wb_models.SupplySale = wb_models.SupplySale(
            id=sl_dict_entry['saleID'],
            order_id=order_info[0],
            order_pos_id=order_info[1],
            nomenclature_id=sl_dict_entry['nmId'],
            srid=(sl_dict_entry['srid'] if sl_dict_entry['srid'] != '' else None),
            warehouse_id=self.check_warehouse(wh_name=sl_dict_entry['warehouseName']),
            variation_id=(var_id if var_id else None),

            date=sl_dict_entry['date'],
            last_change_date=sl_dict_entry['lastChangeDate'],
            supplier_article=sl_dict_entry['supplierArticle'],
            tech_size=sl_dict_entry['techSize'],
            barcode=sl_dict_entry['barcode'],
            total_price=sl_dict_entry['totalPrice'],
            discount_percent=sl_dict_entry['discountPercent'],
            finished_price=sl_dict_entry['finishedPrice'],
            price_with_disc=sl_dict_entry['priceWithDisc'],
            for_pay=sl_dict_entry['forPay'],
            
            income_id=sl_dict_entry['incomeID'],
            is_supply=sl_dict_entry['isSupply'],
            is_realization=sl_dict_entry['isRealization'],
            is_storno=sl_dict_entry.get('IsStorno', 0),
            promo_code_discount=sl_dict_entry.get('promoCodeDiscount', 0),
            spp=sl_dict_entry['spp'],
            sticker=sl_dict_entry['sticker'],
            warehouse=sl_dict_entry['warehouseName'],
            country=sl_dict_entry['countryName'],
            region=sl_dict_entry['regionName']
        )
        return sale_model

    def update_sale_record(self,sale_model_in_db: wb_models.SupplySale, sale_dict: dict) -> None:
        """updates sales record"""
        try:
            assert sale_model_in_db.srid == sale_dict['srid'], f"failed srid assertion for this sale ID - > {sale_dict['saleID']}"
            assert sale_model_in_db.order_id == sale_dict['gNumber'], f"failed gNumber (order_id) assertion for this sale ID - > {sale_dict['saleID']}"
            assert sale_model_in_db.order_pos_id == sale_dict['odid'], f"failed odid (order_pos_id) assertion for this sale ID - > {sale_dict['saleID']}"
            assert sale_model_in_db.nomenclature_id == sale_dict['nmId'], f"failed nomenclature id assertion for this sale ID - > {sale_dict['saleID']}"
            assert sale_model_in_db.warehouse_id == self.check_warehouse(wh_name=sale_dict['warehouseName']), f"failed warehouse id assertion for this sale ID - > {sale_dict['saleID']}"
            assert sale_model_in_db.date.strftime('%Y-%m-%dT%H:%M:%S') == sale_dict['date'], f"failed date assertion for this sale ID - > {sale_dict['saleID']}"
        except AssertionError as e:
                print(e)

        var_id: int = self.check_variation(
            var_id_=''.join([str(sale_dict['nmId']), sale_dict['techSize']]),
            nm_id_=sale_dict['nmId'],
            tech_size_=sale_dict['techSize']
        )

        sale_model_in_db.last_change_date = sale_dict['lastChangeDate']
        sale_model_in_db.supplier_article = sale_dict['supplierArticle']
        sale_model_in_db.tech_size = sale_dict['techSize']
        sale_model_in_db.barcode = sale_dict['barcode']
        sale_model_in_db.total_price = sale_dict['totalPrice']
        sale_model_in_db.discount_percent = sale_dict['discountPercent']
        sale_model_in_db.finished_price = sale_dict['finishedPrice']
        sale_model_in_db.price_with_disc = sale_dict['priceWithDisc']
        sale_model_in_db.for_pay = sale_dict['forPay']
        sale_model_in_db.variation_id=(var_id if var_id else None)
    
        sale_model_in_db.income_id = sale_dict['incomeID']
        sale_model_in_db.is_supply = sale_dict['isSupply']
        sale_model_in_db.is_realization = sale_dict['isRealization']
        sale_model_in_db.is_storno = sale_dict.get('IsStorno', 0)
        sale_model_in_db.promo_code_discount = sale_dict.get('promoCodeDiscount', 0)
        sale_model_in_db.spp = sale_dict['spp']
        sale_model_in_db.sticker = sale_dict['sticker']
        sale_model_in_db.warehouse = sale_dict['warehouseName']
        sale_model_in_db.country = sale_dict['countryName']
        sale_model_in_db.region = sale_dict['regionName']

        try:
            db_session.commit()
        except IntegrityError as e:
            print(f"failed to commit ->", e)

    def process_sale(self, sl_dict_entry: dict) -> None:
        """processes just an order itself, without its positions yet"""
        # getting sales in db
        sale_in_db: wb_models.SupplyOrder = (
            db_session.query(wb_models.SupplySale).filter_by(id=sl_dict_entry['saleID']).first()
        )
        if not sale_in_db:
            model_to_add: wb_models.SupplySale = self.add_new_sale(sl_dict_entry=sl_dict_entry)
            if not model_to_add:
                return False
            try:
                db_session.add(model_to_add)
                db_session.commit()
            except IntegrityError as e:
                print(f"failed to commit ->", e)
            return True
        
        self.update_sale_record(sale_model_in_db=sale_in_db, sale_dict=sl_dict_entry)
        return True

    # def process_sale_position(self, pos_dict_entry: dict) -> None:
    #     """processes just an order itself, without its positions yet"""
    #     def check_warehouse(wh_name: str) -> int:
    #         """checks warehouse in the DB, and if not present adds it to it.
    #         Returns warehouse's ID"""
    #         wh_in_db: wb_models.SupplyWarehouse = db_session.query(wb_models.SupplyWarehouse).filter_by(name=wh_name)
    #         if wh_in_db.first():
    #             if wh_in_db.count() > 1:
    #                 print(f"This warehouse has duplicates in the DB, - > {wh_name}")
    #             return wh_in_db.first().id
    #         return None
        
    #     def check_nomenclature(nm_id_: int) -> bool:
    #         """checks whether a nomenclature is in the new base API, if not, just skips it"""
    #         nm_in_db: wb_models.Nomenclature = db_session.query(wb_models.Nomenclature).filter_by(id=nm_id_).first()
    #         if not nm_in_db:
    #             print(f"This nomenclature is missing from the WB -> {nm_id_}")
    #             return False
    #         return True

    #     order_pos_in_db: wb_models.SupplyOrderPosition = db_session.query(wb_models.SupplyOrderPosition).filter_by(
    #                                                                 id=pos_dict_entry['odid'], order_id=pos_dict_entry['gNumber']
    #                                                             )
    #     if order_pos_in_db.count() > 1:
    #         print(bcolors.FAIL, f"This order has duplicates, check it -> {pos_dict_entry['gNumber']} : {pos_dict_entry['odid']}", bcolors.ENDC)
        
    #     if not check_nomenclature(nm_id_=pos_dict_entry['nmId']):
    #         return False

    #     if not order_pos_in_db.first():
    #         # add order position
    #         position_to_add: wb_models.SupplyOrderPosition = wb_models.SupplyOrderPosition(
    #             id=pos_dict_entry['odid'],
    #             order_id=pos_dict_entry['gNumber'],
    #             nomenclature_id=pos_dict_entry['nmId'],
    #             supplier_article=pos_dict_entry['supplierArticle'],
    #             tech_size=pos_dict_entry['techSize'],
    #             barcode=pos_dict_entry['barcode'],
    #             warehouse_id=(check_warehouse(wh_name=pos_dict_entry['warehouseName'])),
    #             warehouse=pos_dict_entry['warehouseName'],
    #             region=pos_dict_entry['oblast'],
    #             total_price=pos_dict_entry['totalPrice'],
    #             discount_percent=pos_dict_entry['discountPercent'],
    #             is_cancel=pos_dict_entry['isCancel'],
    #             cancel_date=(pos_dict_entry['cancel_dt'] if pos_dict_entry['cancel_dt'] != '0001-01-01T00:00:00' else None),
    #             sticker=(pos_dict_entry['sticker'] if pos_dict_entry['sticker'] != '' else None),
    #             income_id=(pos_dict_entry['incomeID'] if pos_dict_entry['incomeID'] != 0 else None),
    #             last_change_date=pos_dict_entry['lastChangeDate']
    #         )
    #         try:
    #             db_session.add(position_to_add)
    #             db_session.commit()
    #         except IntegrityError as e:
    #             print(f"failed to commit ->", e)
    #         return True
    #     try:
    #         assert order_pos_in_db.first().nomenclature_id == pos_dict_entry['nmId']
    #     except AssertionError as e:
    #             print(f"This warehouse has different representation in the DB and from API -> {pos_dict_entry['nmId']} -- {order_pos_in_db.nomenclature_id}", e)
        
    #     order_pos_in_db.supplier_article = pos_dict_entry['supplierArticle']
    #     order_pos_in_db.tech_size = pos_dict_entry['techSize']
    #     order_pos_in_db.barcode = pos_dict_entry['barcode']
    #     order_pos_in_db.warehouse_id  = (check_warehouse(wh_name=pos_dict_entry['warehouseName']))
    #     order_pos_in_db.warehouse = pos_dict_entry['warehouseName']
    #     order_pos_in_db.region = pos_dict_entry['oblast']
    #     order_pos_in_db.total_price = pos_dict_entry['totalPrice']
    #     order_pos_in_db.discount_percent = pos_dict_entry['discountPercent']
    #     order_pos_in_db.is_cancel = pos_dict_entry['isCancel']
    #     order_pos_in_db.cancel_date = (pos_dict_entry['cancel_dt'] if pos_dict_entry['cancel_dt'] != '0001-01-01T00:00:00' else None)
    #     order_pos_in_db.sticker = (pos_dict_entry['sticker'] if pos_dict_entry['sticker'] != '' else None)
    #     order_pos_in_db.income_id = (pos_dict_entry['incomeID'] if pos_dict_entry['incomeID'] != 0 else None)
    #     order_pos_in_db.last_change_date = pos_dict_entry['lastChangeDate']

    #     try:
    #         db_session.commit()
    #     except IntegrityError as e:
    #         print(f"failed to commit ->", e)

            

    def process_entry(self, dict_entry: dict) -> None:
        """processes each entry"""
        self.process_sale(sl_dict_entry=dict_entry)


class DBSupplyFinReportUpdater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id

    # def convert_decimals(self, price_: str) -> Decimal:
    #     return Decimal(price_[:-2] + '.' + price_[-2:])
    def prep_model(self, schema_: wb_schemas.SupplierFinReport) -> wb_models.SupplyFinReport:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.SupplyFinReport.__dict__ if not i.startswith('_')]
        finrep_schema: dict[str, str] = schema_.dict(by_alias=False)

        if finrep_schema['nm_id'] and finrep_schema['ts_name']:
            var_id_in_db: Optional[wb_models.Variation] = self.db_session.query(wb_models.Variation).filter(
                wb_models.Variation.alt_id == (str(finrep_schema['nm_id']) + finrep_schema['ts_name'])
            ).first()
        else:
            var_id_in_db: Optional[wb_models.Variation] = None
        if finrep_schema['nm_id']:
            nm_in_db: Optional[wb_models.Nomenclature] = self.db_session.query(wb_models.Nomenclature).filter(
                wb_models.Nomenclature.id == finrep_schema['nm_id']
            ).first()
            if not nm_in_db:
                finrep_schema['nm_id'] = None

        finrep_schema['supplier_id'] = self.supp_id
        finrep_schema['id'] = finrep_schema['rrd_id']
        finrep_schema['variation_id'] = (var_id_in_db.id if var_id_in_db else var_id_in_db)

        finrep_schema = {key: value for key, value in finrep_schema.items() if key in req_fields}
        return wb_models.SupplyFinReport(**finrep_schema)

    def check_integrity(self, finrep_model: wb_models.SupplyFinReport) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: wb_models.SupplyFinReport = self.db_session.query(wb_models.SupplyFinReport).filter(
            wb_models.SupplyFinReport.supplier_id == finrep_model.supplier_id,
            wb_models.SupplyFinReport.id == finrep_model.id
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, finrep_model: wb_models.SupplyFinReport) -> None:
        """Updates Product entity"""
        finrep_model: wb_models.SupplyFinReport = self.db_session.query(wb_models.SupplyFinReport).filter(
            wb_models.SupplyFinReport.supplier_id == finrep_model.supplier_id,
            wb_models.SupplyFinReport.id == finrep_model.id
        ).first()

        finrep_model.retail_price = finrep_model.retail_price
        # finrep_model.market_price = finrep_model.market_price
        # finrep_model.currency = finrep_model.currency
        # finrep_model.date_start = finrep_model.date_start
        # finrep_model.date_end = finrep_model.date_end
        
        # finrep_model.export_status = finrep_model.export_status
        # finrep_model.approval_status = finrep_model.approval_status
        # finrep_model.market_price_status = finrep_model.market_price_status

        self.db_session.commit()

        # try:
        #     assert int(product_in_db.price) == int(finrep_model.price), f"for this product {product_in_db.material_number} not the same prices"
        #     assert product_in_db.promo_price == finrep_model.promo_price, f"for this product {product_in_db.material_number} not the same promo prices"
        # except AssertionError as err:
        #     print(err)
        

    def create(self, finrep_model: wb_models.SupplyFinReport) -> None:
        """Creates Product entity"""
        self.db_session.add(finrep_model)
        self.db_session.commit()


class DBBackSupplyStockUpdaterV2:
    """
    """
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id
    
    def check_variation(self, alt_id: str) -> Union[int, bool]:
        """
        checks whether variation is in the db or not
        """
        variation_in_db: wb_models.Variation = db_session.query(wb_models.Variation).filter(
            wb_models.Variation.alt_id == alt_id
        ).first()
        if not variation_in_db:
            print(
                bcolors.FAIL,
                f'Unfortunately this alt id of variation is not present in the DB -> {alt_id}',
                bcolors.ENDC
            )
            return False
        return variation_in_db.id
    
    def get_records(self, schema_: wb_schemas.PostBackV1BalancesResponseData) -> list[dict]:
        REN_COLS = {
            'Бренд': 'brand',
            'Предмет': 'subject',
            'Объем, л': 'volume',
            'Артикул продавца': 'supplier_article',
            'Артикул WB': 'nomenclature_id',
            'Баркод': 'barcode',
            'Размер вещи': 'ts_name',
            'В пути до клиента': 'quantityInTransitToClient',
            'В пути от клиента': 'quantityInTransitFromClient',
            'Итого по складам': 'quantity_for_sale'
        }
        
        df = pd.DataFrame(
            schema_.table.data,
            columns=[cell_.value for cell_ in schema_.table.headerExcel[0].cells]
        )
        df = df.rename(columns=REN_COLS)
        df = df[df.columns.difference(['brand', 'subject', 'volume'])]
        warehouses = list(df[df.columns.difference(list(REN_COLS.values()))].columns)
        df[['quantityInTransitToClient', 'quantityInTransitFromClient', 'quantity_for_sale']] = df[['quantityInTransitToClient', 'quantityInTransitFromClient', 'quantity_for_sale']].replace('', 0).applymap(int)
        df['quantity_in_transit'] = df['quantityInTransitFromClient'] + df['quantityInTransitToClient']
        tdf = pd.melt(
            frame=df[df.columns.difference([
                'quantity_for_sale', 'quantity_in_transit',
                'quantityInTransitFromClient', 'quantityInTransitToClient'
            ])],
            id_vars=['nomenclature_id', 'barcode', 'supplier_article', 'ts_name'],
            var_name='warehouse',
            value_name='quantity_for_sale'
        )
        tdf['quantity_for_sale'] = tdf['quantity_for_sale'].replace('', 0).map(int)
        tdf = pd.merge(
            tdf,
            df[['nomenclature_id', 'ts_name', 'quantity_in_transit']],
            on=['nomenclature_id', 'ts_name'],
            how='left')
        return tdf.to_dict(orient='records')




    def prep_model(self, schema_: dict) -> wb_models.BackSupplyStock:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.BackSupplyStock.__dict__ if not i.startswith('_')]
        back_balances_schema: dict[str, str] = schema_

        alt_id: str = (str(back_balances_schema['nomenclature_id']) + str(back_balances_schema['ts_name']))
        var_id = self.check_variation(alt_id=alt_id)
        if not var_id:
            return False
        
        back_balances_schema['variation_id'] = var_id

        back_balances_schema = {key: value for key, value in back_balances_schema.items() if key in req_fields}
        return wb_models.BackSupplyStock(**back_balances_schema)

    def check_integrity(self, back_supply_stock_model: wb_models.BackSupplyStock) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: wb_models.BackSupplyStock = self.db_session.query(wb_models.BackSupplyStock).filter(
            wb_models.BackSupplyStock.variation_id == back_supply_stock_model.variation_id,
            wb_models.BackSupplyStock.warehouse == back_supply_stock_model.warehouse,
            wb_models.BackSupplyStock.updated_at == datetime.now().date()
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, back_supply_stock_model: wb_models.BackSupplyStock) -> None:
        """Updates Product entity"""
        back_supply_stock_model: wb_models.BackSupplyStock = self.db_session.query(wb_models.BackSupplyStock).filter(
            wb_models.BackSupplyStock.variation_id == back_supply_stock_model.variation_id,
            wb_models.BackSupplyStock.warehouse == back_supply_stock_model.warehouse,
            wb_models.BackSupplyStock.updated_at == datetime.now().date()
        ).first()

        back_supply_stock_model.quantity_for_sale = back_supply_stock_model.quantity_for_sale
        back_supply_stock_model.quantity_in_transit = back_supply_stock_model.quantity_in_transit

        self.db_session.commit()
        

    def create(self, back_supply_stock_model: wb_models.BackSupplyStock) -> None:
        """Creates Product entity"""
        self.db_session.add(back_supply_stock_model)
        self.db_session.commit()

    def refresh(self, schema_: wb_schemas.PostBackV1BalancesResponseData) -> None:
        def refresh_per_record(record: dict) -> None:
            back_supply_stock_model = self.prep_model(schema_=record)
            if not back_supply_stock_model:
                return None
            if self.check_integrity(back_supply_stock_model):
                self.update(back_supply_stock_model)
                return None
            self.create(back_supply_stock_model)
            return None
        
        records = self.get_records(schema_=schema_)
        for record_ in records:
            refresh_per_record(record=record_)
            

class DBOrderStickerUpdater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession) -> None:
        self.sesh = client_session
        self.db_session = db_session

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id
    
    def set_order_ticker_in_db(self, order_id: int) -> None:
        order_in_db: wb_models.Order = self.db_session.query(wb_models.Order).filter(wb_models.Order.id == order_id).first()
        if not order_in_db:
            print(f"This order sticker doesn't have order relation in db -> {order_id}")
            return None
        order_in_db.has_sticker = True
        self.db_session.commit()

    
    def prep_model(self, schema_: wb_schemas.GetOrdersStickersSticker) -> wb_models.OrderSticker:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.OrderSticker.__dict__ if not i.startswith('_')]
        order_sticker_schema: dict[str, str] = schema_.dict(by_alias=False)

        order_sticker_schema['supplier_id'] = self.supp_id

        order_sticker_schema = {key: value for key, value in order_sticker_schema.items() if key in req_fields}
        return wb_models.OrderSticker(**order_sticker_schema)

    def check_integrity(self, order_sticker_model: wb_models.OrderSticker) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        prod_in_db: wb_models.OrderSticker = self.db_session.query(wb_models.OrderSticker).filter(
            wb_models.OrderSticker.supplier_id == order_sticker_model.supplier_id,
            wb_models.OrderSticker.order_id == order_sticker_model.order_id
        ).first()
        if prod_in_db:
            return True
        return False

    def update(self, order_sticker_model: wb_models.OrderSticker) -> None:
        """Updates Product entity"""
        order_sticker_model: wb_models.OrderSticker = self.db_session.query(wb_models.OrderSticker).filter(
            wb_models.OrderSticker.supplier_id == order_sticker_model.supplier_id,
            wb_models.OrderSticker.order_id == order_sticker_model.order_id
        ).first()

        order_sticker_model.part_a = order_sticker_model.part_a
        order_sticker_model.part_b = order_sticker_model.part_b
        order_sticker_model.barcode = order_sticker_model.barcode
        self.db_session.commit()

    def create(self, order_sticker_model: wb_models.OrderSticker) -> None:
        """Creates Product entity"""
        self.db_session.add(order_sticker_model)
        self.db_session.commit()

        self.set_order_ticker_in_db(order_id=order_sticker_model.order_id)


    def refresh(self, schema_: wb_schemas.GetOrdersStickersSticker) -> None:
        order_sticker_model = self.prep_model(schema_=schema_)
        if self.check_integrity(order_sticker_model):
            self.update(order_sticker_model)
            return None
        self.create(order_sticker_model)
        return None


class DBNomenclaturePriceV2Updater:
    """writes and updates supply orders (those from statistics API) into the
    DB. two part process consisting of writing order first and then its po-
    sitions with nomenclatures."""
    def __init__(self, client_session: ClientSession, extraction_ts: datetime) -> None:
        self.sesh = client_session
        self.db_session = db_session
        self.extraction_ts = extraction_ts

    @property
    def supp_id(self) -> int:
        """gets supplier id as integer"""
        supplier_uuid: str = self.sesh.supplier.id
        supplier_id: int = db_session.query(wb_models.Supplier).filter_by(uuid=supplier_uuid).first().id
        return supplier_id
    
    def check_nm_id(self, nm_id: int) -> bool:
        nm_id_in_db: int = db_session.query(wb_models.Nomenclature).filter(
            wb_models.Nomenclature.id == int(nm_id)
        ).first()
        if not nm_id_in_db:
            return False
        return True
    
    def check_chrt_id(self, chrt_id: int) -> bool:
        chrt_id_in_db: int = db_session.query(wb_models.Variation).filter(
            wb_models.Variation.id == int(chrt_id)
        ).first()
        if not chrt_id_in_db:
            return False
        return True
    

    def prep_model(self, schema_: dict) -> wb_models.NomenclaturePriceV2 | None:
        """prepares ORM model for a given schema"""
            
        req_fields: list[str] = [i for i in wb_models.NomenclaturePriceV2.__dict__ if not i.startswith('_')]
        nomenclature_price_v2_schema: dict[str, str] = schema_
        nomenclature_price_v2_schema['supplier_id'] = self.supp_id
        nomenclature_price_v2_schema['report_date'] = datetime.now().date()
        nomenclature_price_v2_schema['extracted_at'] = self.extraction_ts

        check_nm_in_db = self.check_nm_id(nm_id=nomenclature_price_v2_schema['nomenclature_id'])
        check_chrt_in_db = self.check_chrt_id(chrt_id=nomenclature_price_v2_schema['variation_id'])
        
        if (not check_nm_in_db) or (not check_chrt_in_db):
            unrecognized_prod_repr: str = f"""
                        supplier_article={nomenclature_price_v2_schema['vendor_code']},
                        tech_size={nomenclature_price_v2_schema['tech_size_name']},
                        nm_id={nomenclature_price_v2_schema['nomenclature_id']},
                        chrt_id={nomenclature_price_v2_schema['variation_id']}"""
            print(
                f"There is unrecognized product -> {unrecognized_prod_repr}"
            )
            return None

        nomenclature_price_v2_schema = {key: value for key, value in nomenclature_price_v2_schema.items() if key in req_fields}
        return wb_models.NomenclaturePriceV2(**nomenclature_price_v2_schema)

    def check_integrity(self, nomenclature_price_v2_model: wb_models.NomenclaturePriceV2) -> bool:
        """
        Checks integrity, if True = create False = update
        """
        nomenclature_price_v2_in_db: wb_models.NomenclaturePriceV2 = self.db_session.query(wb_models.NomenclaturePriceV2).filter(
            wb_models.NomenclaturePriceV2.supplier_id == nomenclature_price_v2_model.supplier_id,
            wb_models.NomenclaturePriceV2.variation_id == nomenclature_price_v2_model.variation_id,
            wb_models.NomenclaturePriceV2.report_date == nomenclature_price_v2_model.report_date
        ).first()
        if nomenclature_price_v2_in_db:
            return True
        return False

    def update(self, nomenclature_price_v2_model: wb_models.NomenclaturePriceV2) -> None:
        """Updates Product entity"""
        nomenclature_price_v2_model: wb_models.NomenclaturePriceV2 = self.db_session.query(wb_models.NomenclaturePriceV2).filter(
            wb_models.NomenclaturePriceV2.supplier_id == nomenclature_price_v2_model.supplier_id,
            wb_models.NomenclaturePriceV2.variation_id == nomenclature_price_v2_model.variation_id,
            wb_models.NomenclaturePriceV2.report_date == nomenclature_price_v2_model.report_date
        ).first()

        nomenclature_price_v2_model.price = nomenclature_price_v2_model.price
        nomenclature_price_v2_model.discount = nomenclature_price_v2_model.discount
        nomenclature_price_v2_model.discounted_price = nomenclature_price_v2_model.discounted_price

        self.db_session.commit()

    def create(self, nomenclature_price_v2_model: wb_models.NomenclaturePriceV2) -> None:
        """Creates Product entity"""
        self.db_session.add(nomenclature_price_v2_model)
        self.db_session.commit()

    def refresh(self, schema_: wb_schemas.GetOrdersStickersSticker) -> None:
        nomenclature_price_v2_model = self.prep_model(schema_=schema_)
        if not nomenclature_price_v2_model:
            return None
        if self.check_integrity(nomenclature_price_v2_model):
            self.update(nomenclature_price_v2_model)
            return None
        self.create(nomenclature_price_v2_model)
        return None