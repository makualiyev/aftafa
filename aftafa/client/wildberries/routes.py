from datetime import datetime, date, timedelta
import json
import time
from typing import Sequence, Tuple, Generator, Union
from itertools import chain
from collections import Counter

from sqlalchemy import exc, select
from sqlalchemy.exc import IntegrityError
from pydantic import UUID4, ValidationError
from requests.models import Response
from requests.exceptions import JSONDecodeError

import aftafa.client.wildberries.models as wb_models
from aftafa.client.wildberries.models import session as db_session
import aftafa.client.wildberries.schemas as wb_schemas
from aftafa.client.wildberries.client import ClientSupplier, ClientSession, ClientMethod, ClientDirectSession
from aftafa.client.wildberries.crud import (
    DBCardUpdater,
    DBV2CardUpdater,
    DBPriceUpdater,
    DBStockUpdater,
    DBSupplyOrderUpdater,
    DBSupplySaleUpdater,
    DBBackSupplyStockUpdater,
    DBSupplyOrderV2Updater,
    DBSupplySaleV2Updater,
    DBSupplyUpdater,
    DBSupplyStockV2Updater,
    DBSupplyFinReportUpdater,
    DBOrderUpdater,
    DBWarehouseUpdater,
    DBBackSupplyStockUpdaterV2,
    DBOrderStickerUpdater,
    DBNomenclaturePriceV2Updater
)
from aftafa.utils.helpers import bcolors, split_into_chunks

class PostCardsList(ClientMethod):
    def __init__(
        self,
        limit: int = 1000,
        offset: int = 0,
        nm_id_ : int = None
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/content/v1/cards/list', 'account')
        
        self.body = {
            "sort": {
                "limit": limit,
                "offset": offset,
                "searchValue": nm_id_
            }
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.post(self.url, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.RequestCardList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        session.prep_req(client_method=self)
        i: int = 0
        ticker: int = 1

        while ticker != 0:
            self.body['sort']['offset'] = (i * 1_000)
            with session.post(self.url, json=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    ticker = 1 if (len(response.json()['data']['cards']) // 1_000) == 1 else 0
                    i += 1
                    yield response
                elif response.status_code == 429:
                    time.sleep(10)
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        card_updater: DBCardUpdater = DBCardUpdater(client_session=session)

        for card_chunk in self.get_chunks(session=session):
            if card_chunk:
                for card_ in card_chunk.json()['data']['cards']:
                    card_updater.process_card_from_list(card_list_entry=card_)


class PostCardsCursorList(ClientMethod):
    def __init__(
        self,
        limit: int = 1000,
        nm_id_ : int = None,
        updated_at_: str = None,
        text_search: int = "",
        with_photo: int = -1,
        sort_column: str = None,
        ascending: bool = None
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/content/v1/cards/cursor/list', 'account')
        
        self.body = {
                'sort': {
                    'cursor': {
                        'updatedAt': updated_at_,
                        'nmID': nm_id_,
                        'limit': limit
                    },
                    'filter': {
                        'textSearch': text_search,
                        'withPhoto': with_photo,
                    },
                    'sort': {
                        'sortColumn': sort_column,
                        'ascending': ascending
                    }
                }
            }

    def make_request(self, session : ClientSession, **kwargs) -> Response:
        session.prep_req(client_method=self)
        self.body.update(**kwargs)

        with session.post(self.url, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.RequestCardCursorList(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        session.prep_req(client_method=self)
        ticker: int = 1
        load = lambda updated_at_, nm_id_: {
                        'sort': {
                            'cursor': {
                                'updatedAt': updated_at_,
                                'nmID': nm_id_
                                }
                            }
                        }

        while ticker != 0:
            # self.body['sort']['offset'] = (i * 1_000)
            with session.post(self.url, json=self.body) as response:
                
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    ticker = 1 if (response.json()['data']['cursor']['total'] // 1_000) == 1 else 0
                    if ticker == 1:
                        self.body.update(
                            **load(
                                updated_at_=response.json()['data']['cursor']['updatedAt'],
                                nm_id_=response.json()['data']['cursor']['nmID']
                            )
                        )
                    yield response
                elif response.status_code == 429:
                    time.sleep(10)
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        card_updater: DBCardUpdater = DBCardUpdater(client_session=session)

        for card_chunk in self.get_chunks(session=session):
            if card_chunk:
                for card_ in card_chunk.json()['data']['cards']:
                    card_updater.process_card_from_list(card_list_entry=card_)


class PostContentV2GetCardsList(ClientMethod):
    def __init__(
        self,
        limit: int = 100,
        imt_id_ : int | None = None,
        nm_id_: int | None = None,
        updated_at_: str | None = None,
        text_search: int = "",
        with_photo: int = -1,
        tag_ids: list[int] | None = None,
        object_ids: list[int] | None = None,
        brands: list[str] | None = None,
        ascending: bool = False
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/content/v2/get/cards/list', 'account')
        
        self.body = {
            'settings': {
                'sort': {
                    'ascending': ascending
                },
                'filter': {
                    'withPhoto': with_photo,
                    'textSearch': text_search,
                    'tagIDs': tag_ids,
                    'allowedCategoriesOnly': False,
                    'objectIDs': object_ids,
                    'brands': brands,
                    'imtID': imt_id_
                },
                'cursor': {
                    'updatedAt': updated_at_,
                    'nmID': nm_id_,
                    'limit': limit
                }
            }
        }

    def make_request(self, session : ClientSession, **kwargs) -> Response:
        session.prep_req(client_method=self)
        self.body.update(**kwargs)

        with session.post(self.url, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                with content -> {response.content}')
            return response

    def validate_response(self, response : Response):
        try:
            wb_schemas.PostContentV2GetCardsListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        # ...
        session.prep_req(client_method=self)
        ticker: int = 1
        load = lambda updated_at_, nm_id_: {
                        'settings': {
                            'cursor': {
                                'updatedAt': updated_at_,
                                'nmID': nm_id_
                                }
                            }
                        }

        while ticker != 0:
            # self.body['sort']['offset'] = (i * 1_000)
            with session.post(self.url, json=self.body) as response:
                
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    ticker = 1 if (response.json()['cursor']['total'] == 100) else 0
                    if ticker == 1:
                        # self.body.update(
                        #     **load(
                        #         updated_at_=response.json()['cursor']['updatedAt'],
                        #         nm_id_=response.json()['cursor']['nmID']
                        #     )
                        # )
                        self.body['settings']['cursor']['updatedAt'] = response.json()['cursor']['updatedAt']
                        self.body['settings']['cursor']['nmID'] = response.json()['cursor']['nmID']
                    yield response
                elif response.status_code == 429:
                    time.sleep(10)
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        ...
        card_updater: DBV2CardUpdater = DBV2CardUpdater(client_session=session)

        for card_chunk in self.get_chunks(session=session):
            if card_chunk:
                for card_ in card_chunk.json()['cards']:
                    card_updater.process_card_from_list(card_list_entry=card_)
                    card_updater.process_card_from_filter(card_filter_entry=card_)


class PostCardsFilter(ClientMethod):
    def __init__(self, vendor_codes: list[str] = None) -> None:
        ClientMethod.__init__(self, 'POST', '/content/v1/cards/filter', 'account')
        self.body = {
            "vendorCodes": vendor_codes
        }

    def make_request(self, session : ClientSession, **kwargs) -> Response:
        session.prep_req(client_method=self)
        self.body.update(**kwargs)

        with session.post(self.url, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.RequestCardFilter(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession, load: list[str] | None) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        def split_into_chunks(lst : list, n_size : int) -> Generator[Response, None, None]:
            """Used to split product ids into small chunks of a size 100"""
            for i in range(0, len(lst), n_size):
                yield lst[i:i + n_size]

        for chunk in split_into_chunks(lst=load, n_size=100):
            yield self.make_request(session=session, **{'vendorCodes': chunk})


    def process_to_db(self, session: ClientSession, load: list[str] | None) -> None:
        """processes cards from filetr into the DB"""
        card_updater: DBCardUpdater = DBCardUpdater(client_session=session)

        for card_chunk in self.get_chunks(session=session, load=load):
            if card_chunk:
                for card_ in card_chunk.json()['data']:
                    card_updater.process_card_from_filter(card_filter_entry=card_)


class GetPriceInfo(ClientMethod):
    def __init__(
        self,
        qty: int = 0
    ) -> None:
        """quantity can take 3 possible flags, 2 - товар с нулевым остатком, 1 - товар с ненулевым остатком,
        0 - товар с любым остатком"""
        
        ClientMethod.__init__(self, 'GET', '/public/api/v1/info', 'prices')
        
        self.body = {
            "quantity" : qty
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for info_entry in response.json():
                wb_schemas.PriceInfo(**info_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        price_updater: DBPriceUpdater = DBPriceUpdater(client_session=session)
        for price_info in self.make_request(session=session).json():
            price_updater.process_entry(dict_entry=price_info)


class GetWarehouseInfo(ClientMethod):
    def __init__(
        self
    ) -> None:
        """no params"""
        
        ClientMethod.__init__(self, 'GET', '/api/v3/warehouses', 'account')
        
        self.body = {}

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for info_entry in response.json():
                wb_schemas.Warehouse(**info_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        wh_updater: DBWarehouseUpdater = DBWarehouseUpdater(client_session=session)
        for wh_info in self.make_request(session=session).json():
            wh_updater.process_entry(dict_entry=wh_info)


class PostStocksByWarehouse(ClientMethod):
    def __init__(
        self,
        warehouse_id: str,
        barcodes: list[str] = ['']
    ) -> None:
        """no params"""
        ClientMethod.__init__(self, 'POST', '/api/v3/stocks/{}', 'account')
        self.warehouse_id = warehouse_id
        self.body = {'skus': barcodes}

    def make_request(self, session : ClientSession, **kwargs) -> Response:
        session.prep_req(client_method=self)
        self.body.update(**kwargs)

        with session.post(self.url.format(self.warehouse_id), json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.PostStocksByWarehouseResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession, load: list[str] | None) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        def split_into_chunks(lst : list, n_size : int) -> Generator[Response, None, None]:
            """Used to split product ids into small chunks of a size 100"""
            for i in range(0, len(lst), n_size):
                yield lst[i:i + n_size]

        for chunk in split_into_chunks(lst=load, n_size=1000):
            yield self.make_request(session=session, **{'skus': chunk})

    def process_to_db(self, session: ClientSession) -> None:
        pass
        # wh_updater: DBWarehouseUpdater = DBWarehouseUpdater(client_session=session)
        # for wh_info in self.make_request(session=session).json():
        #     wh_updater.process_entry(dict_entry=wh_info)


class GetOrders(ClientMethod):
    def __init__(
        self,
        limit: int = 1000,
        next: int = 0,
        date_from: str | None = None, # %Y-%m-%d
        date_to: str | None = None, # %Y-%m-%d
        flag: int = 0
    ) -> None:
        """
        limit to 1000 and next is int for page
        datefrom and dateto in format of unix timestamp
        flag :param: - 0 is get yesterday's date, 1 is get 7 days
        """
        
        ClientMethod.__init__(self, 'GET', '/api/v3/orders', 'account')
        self.params = {
            'limit': limit,
            'next': next,
            'dateFrom': (self.convert_date(date_from) if date_from else None),
            'dateTo': (self.convert_date(date_to) if date_to else None)
        }

    def convert_date(self, date_: str):
        return int(datetime.strptime(date_, '%Y-%m-%d').timestamp())

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.GetOrders(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """
        """
        session.prep_req(client_method=self)
        next_: int = 0
        check_: int = 0

        while not check_:
            self.params.update({'next': next_})
            with session.get(self.url, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')
            if len(response.json()['orders']) >= 1000:
                next_ = response.json()['next']
                continue
            check_ = 1


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        order_updater: DBOrderUpdater = DBOrderUpdater(client_session=session)
        
        for chunk in self.get_chunks(session=session):
            for order_entry in chunk.json()['orders']:
                order_model = order_updater.prep_model(schema_=wb_schemas.GetOrdersOrder(**order_entry))
                if order_updater.check_integrity(order_model=order_model):
                    order_updater.update(order_model)
                else:
                    order_updater.create(order_model)


class GetSupplies(ClientMethod):
    def __init__(
        self,
        limit: int = 1000,
        next: int = 0
    ) -> None:
        """no params"""
        
        ClientMethod.__init__(self, 'GET', '/api/v3/supplies', 'account')
        
        self.params = {
            'limit': limit,
            'next': next
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.GetSupplies(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """
        """
        session.prep_req(client_method=self)
        next_: int = 0
        check_: int = 0

        while not check_:
            self.params.update({'next': next_})
            with session.get(self.url, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')
            if len(response.json()['supplies']) >= 1000:
                next_ = response.json()['next']
                continue
            check_ = 1


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_updater: DBSupplyUpdater = DBSupplyUpdater(client_session=session)
        
        for chunk in self.get_chunks(session=session):
            for supply_info in chunk.json()['supplies']:
                supply_updater.process_entry(dict_entry=supply_info)


class GetSuppliesSupplyOrders(ClientMethod):
    def __init__(
        self,
        supply: str
    ) -> None:
        """no params"""
        
        ClientMethod.__init__(self, 'GET', '/api/v3/supplies/{}/orders', 'account')
        
        self.supply = supply
        self.params = {}

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url.format(self.supply)) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.GetSuppliesSupplyOrders(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """
        """
        return None
        session.prep_req(client_method=self)
        next_: int = 0
        check_: int = 0

        while not check_:
            self.params.update({'next': next_})
            with session.get(self.url, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')
            if len(response.json()['supplies']) >= 1000:
                next_ = response.json()['next']
                continue
            check_ = 1


    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        return None
        supply_updater: DBSupplyUpdater = DBSupplyUpdater(client_session=session)
        
        for chunk in self.get_chunks(session=session):
            for supply_info in chunk.json()['supplies']:
                supply_updater.process_entry(dict_entry=supply_info)


class GetOrdersStickers(ClientMethod):
    def __init__(
        self,
        orders_list: list[int],
    ) -> None:
        """
        limit to 1000 and next is int for page
        datefrom and dateto in format of unix timestamp
        flag :param: - 0 is get yesterday's date, 1 is get 7 days
        """
        
        ClientMethod.__init__(self, 'GET', '/api/v3/orders/stickers', 'account')
        self.params = {
            'type': 'png',
            'width': 58,
            'height': 40
        }
        self.body = {
            'orders': orders_list
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.post(self.url, params=self.params, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.GetOrdersStickers(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """
        """
        chunks = split_into_chunks(
                [mod_.id for mod_ in db_session.query(wb_models.Order).filter(
                        wb_models.Order.supplier_id == 1,
                        wb_models.Order.has_sticker == False
                    ).all()],
                        100    
                    )
        for chunk in chunks:
            session.prep_req(client_method=self)
            self.body.update({'orders' : chunk})
        
            with session.post(self.url, params=self.params, json=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")
                    

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        order_sticker_updater: DBOrderStickerUpdater = DBOrderStickerUpdater(client_session=session)

        for chunk in self.get_chunks(session=session):
            for sticker in chunk.json()['stickers']:
                order_sticker_updater.refresh(schema_=wb_schemas.GetOrdersStickersSticker(**sticker))



class GetStatSupplierStocks(ClientMethod):
    def __init__(
        self, 
        date_from: str = datetime.today().strftime("%Y-%m-%d")
    ) -> None:
        """takes one argument - date as a string"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/stocks', 'stats')
        
        self.body = {
            "dateFrom" : date_from
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierStocks(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        stock_updater: DBStockUpdater = DBStockUpdater(client_session=session)
        for stock_info in self.make_request(session=session).json():
            stock_updater.process_entry(dict_entry=stock_info)


class GetStatSupplierStocksV2(ClientMethod):
    def __init__(
        self, 
        # date_from: str = datetime.today().strftime("%Y-%m-%d")
        date_from: str = '2020-01-01'
    ) -> None:
        """takes one argument - date as a string"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/stocks', 'stats')
        
        self.body = {
            "dateFrom" : date_from
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierStocks(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_stock_v2_writer: DBSupplyStockV2Updater = DBSupplyStockV2Updater(client_session=session, extraction_ts=datetime.today())
        response = self.make_request(session=session)
        chunk = response.json()
        
        for supply_stock_v2_entry in chunk:
            stock_v2_model = supply_stock_v2_writer.prep_model(schema_=wb_schemas.SupplierStocks(**supply_stock_v2_entry))
            # if supply_stock_v2_writer.check_integrity(stock_v2_model=stock_v2_model):
            #     supply_stock_v2_writer.update(stock_v2_model)
            # else:
            supply_stock_v2_writer.create(stock_v2_model)


        print(bcolors.OKGREEN + f'Processed {len(chunk)} supply stocks v2 successfully!' + bcolors.ENDC)


class GetStatSupplierOrders(ClientMethod):
    def __init__(
        self,
        date_from: str = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d"),
        # date_from: str = datetime.today().strftime("%Y-%m-%d"),
        flag_: int = 1
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all orders started as of date,
        otherwise (0) it fetches orders, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/orders', 'stats')
        
        self.body = {
            "dateFrom" : date_from,
            "flag" : flag_
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                return response

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierOrders(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_order_updater: DBSupplyOrderUpdater = DBSupplyOrderUpdater(client_session=session)
        result: list[wb_schemas.SupplierOrders] = self.make_request(session=session).json()
        for supply_order_info in result:
            supply_order_updater.process_entry(dict_entry=supply_order_info)
        print(bcolors.OKGREEN + f'Processed {len(result)} supply orders successfully!' + bcolors.ENDC)
            # if not nm_in_db:
            #     try:
            #         response = GetCardsList(nm_id_=nm_id_).make_request(session=self.sesh)
            #         card_result = response.json()['result']['cards']
            #         if card_result:
            #             GetCardsList(nm_id_=nm_id_).process_to_db(session=self.sesh)
            #     except AttributeError:
            #         print(f"This nomenclature is missing from the WB -> {nm_id_}")
            #         return False
        

class GetStatSupplierOrdersV2(ClientMethod):
    def __init__(
        self,
        date_from: str = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d"),
        # date_from: str = datetime.today().strftime("%Y-%m-%d"),
        flag_: int = 1
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all orders started as of date,
        otherwise (0) it fetches orders, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/orders', 'stats')
        
        self.body = {
            "dateFrom" : date_from,
            "flag" : flag_
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            elif response.status_code == 429:
                print('[INFO] 429 status code, waiting for 30 seconds ...')
                time.sleep(30)
                return self.make_request(session=session)
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                return response

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierOrdersV2(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_order_v2_writer: DBSupplyOrderV2Updater = DBSupplyOrderV2Updater(client_session=session)
        response = self.make_request(session=session)
        chunk = response.json()
        
        for supply_order_v2_entry in chunk:
            order_v2_model = supply_order_v2_writer.prep_model(schema_=wb_schemas.SupplierOrdersV2(**supply_order_v2_entry))
            if not order_v2_model:
                continue
            if supply_order_v2_writer.check_integrity(order_v2_model=order_v2_model):
                supply_order_v2_writer.update(order_v2_model)
            else:
                supply_order_v2_writer.create(order_v2_model)


        print(bcolors.OKGREEN + f'Processed {len(chunk)} supply orders v2 successfully!' + bcolors.ENDC)


class GetStatSupplierSalesV2(ClientMethod):
    def __init__(
        self,
        date_from: str = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d"),
        # date_from: str = datetime.today().strftime("%Y-%m-%d"),
        flag_: int = 1
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all orders started as of date,
        otherwise (0) it fetches orders, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/sales', 'stats')
        
        self.body = {
            "dateFrom" : date_from,
            "flag" : flag_
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            elif response.status_code == 429:
                print('[INFO] 429 status code, waiting for 30 seconds ...')
                time.sleep(30)
                return self.make_request(session=session)
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                return response

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierSales(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_sale_v2_writer: DBSupplySaleV2Updater = DBSupplySaleV2Updater(client_session=session)
        response = self.make_request(session=session)
        chunk = response.json()
        
        for supply_sale_v2_entry in chunk:
            sale_v2_model = supply_sale_v2_writer.prep_model(schema_=wb_schemas.SupplierSales(**supply_sale_v2_entry))
            if supply_sale_v2_writer.check_integrity(sale_v2_model=sale_v2_model):
                supply_sale_v2_writer.update(sale_v2_model)
            else:
                supply_sale_v2_writer.create(sale_v2_model)


        print(bcolors.OKGREEN + f'Processed {len(chunk)} supply sales v2 successfully!' + bcolors.ENDC)


class GetStatSupplierSales(ClientMethod):
    def __init__(
        self,
        date_from: str = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d"),
        flag_: int = 1
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all sales started as of date,
        otherwise (0) it fetches sales, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/sales', 'stats')
        
        self.body = {
            "dateFrom" : date_from,
            "flag" : flag_
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                return response

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierSales(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        supply_order_updater: DBSupplySaleUpdater = DBSupplySaleUpdater(client_session=session)
        for supply_order_info in self.make_request(session=session).json():
            supply_order_updater.process_entry(dict_entry=supply_order_info)

            # if not nm_in_db:
            #     try:
            #         response = GetCardsList(nm_id_=nm_id_).make_request(session=self.sesh)
            #         card_result = response.json()['result']['cards']
            #         if card_result:
            #             GetCardsList(nm_id_=nm_id_).process_to_db(session=self.sesh)
            #     except AttributeError:
            #         print(f"This nomenclature is missing from the WB -> {nm_id_}")
            #         return False


class GetStatSupplierFinReport(ClientMethod):
    def __init__(
        self,
        date_from: str = datetime.today().strftime("%Y-%m-%d"),
        date_to: str = datetime.today().strftime("%Y-%m-%d"),
        rrdid: int = 0,
        limit: int = 1000
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all orders started as of date,
        otherwise (0) it fetches orders, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v1/supplier/reportDetailByPeriod', 'stats')
        
        self.dates_fmt = {'date_from': datetime.strptime(date_from, "%Y-%m-%d").strftime("%d-%m-%Y"),
        'date_to': datetime.strptime(date_to, "%Y-%m-%d").strftime("%d-%m-%Y")}
        self.body = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "rrdid": rrdid,
            "limit": limit
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierFinReport(**_entry)
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        session.prep_req(client_method=self)
        rrdid: str = '0'
        page_count: int = 1000

        while page_count >= 1000:
            self.body.update({'rrdid' : rrdid})
            time.sleep(2)
            with session.get(self.url, params=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if (not response.json()) or (not len(response.json())):
                        print(f"This method returned nothing")
                        return False
                    page_count = len(response.json())
                    rrdid: str = str(response.json()[-1]['rrd_id'])
                    yield response
                else:
                    print(f"Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}")
                    if response.status_code == 429:
                        time.sleep(100)
                    else:
                        break

    def to_file(self, session: ClientSession, output: str) -> None:
        """Saving to a flat file"""
        chunks: list = []
        for chunk in self.get_chunks(session=session):
            chunks.append(chunk.json())
        result: list = list(chain.from_iterable(chunks))
        file_name = f"wb_financial_{self.dates_fmt['date_from']}_{self.dates_fmt['date_to']}.json"
        
        try:
            with open((output + r'/' + file_name), 'w', encoding='utf-8') as f:
                json.dump(result, f)
                print("Successfully saved file")
        except TypeError:
            print(f"Error - path - {(output + r'/' + file_name)}")

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        finrep_writer: DBSupplyFinReportUpdater = DBSupplyFinReportUpdater(client_session=session)

        for chunk in self.get_chunks(session=session):
            for finrep_entry in chunk.json():
                finrep_model = finrep_writer.prep_model(schema_=wb_schemas.SupplierFinReport(**finrep_entry))
                if finrep_writer.check_integrity(finrep_model=finrep_model):
                    finrep_writer.update(finrep_model)
                else:
                    finrep_writer.create(finrep_model)
        # for supply_order_info in self.make_request(session=session).json():
        #     supply_order_updater.process_entry(dict_entry=supply_order_info)

            # if not nm_in_db:
            #     try:
            #         response = GetCardsList(nm_id_=nm_id_).make_request(session=self.sesh)
            #         card_result = response.json()['result']['cards']
            #         if card_result:
            #             GetCardsList(nm_id_=nm_id_).process_to_db(session=self.sesh)
            #     except AttributeError:
            #         print(f"This nomenclature is missing from the WB -> {nm_id_}")
            #         return False


class PostBackV1Balances(ClientMethod):
    def __init__(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> None:
        """
        """
        ClientMethod.__init__(self, 'POST', '/ns/balances/analytics-back/api/v1/balances', 'back')
        self.params = {
            "limit": limit,
            "offset": offset
        }
        self.body = {
            'filters': [
                "brand",
                "subject",
                "supplierArticle",
                "nmId",
                "barcode",
                "techSize",
                "quantityInTransit",
                "quantityForSaleTotal"
            ]
        }

    def make_request(self, session: ClientDirectSession) -> Response:
        with session.post(self.url, params=self.params, json=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                return response

    def get_chunks(self, session: ClientDirectSession) -> Generator[Response, None, None]:
        check: int = 1
        # offset: int = 0
        i: int = 0

        while check:
            self.params.update({'offset': i})
            with session.post(self.url, params=self.params, json=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    count: int = response.json()['data']['table']['count']
                    if (count - i) // 100 < 1:
                        check = 0
                    i += 100
                    yield response
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                    return response



    def validate_response(self, response : Response):
        try:
            wb_schemas.PostBackV1BalancesResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientDirectSession) -> None:
        """processes cards into the DB"""

        back_stock_updater: DBBackSupplyStockUpdaterV2 = DBBackSupplyStockUpdaterV2(client_session=session)
        
        for chunk in self.get_chunks(session=session):
            back_stock_updater.refresh(
                schema_=wb_schemas.PostBackV1BalancesResponseData(**chunk.json()['data']))

        print(bcolors.OKGREEN + f'Processed back balances stock successfully!' + bcolors.ENDC)

        # result: list[wb_schemas.SupplierOrders] = self.make_request(session=session).json()
        # for supply_order_info in result:
        #     supply_order_updater.process_entry(dict_entry=supply_order_info)
        

class GetStatV3SupplierFinReport(ClientMethod):
    def __init__(
        self,
        date_from: str = datetime.today().strftime("%Y-%m-%d"),
        date_to: str = datetime.today().strftime("%Y-%m-%d"),
        rrdid: int = 0,
        limit: int = 1000
    ) -> None:
        """takes arguments - date as a string, and flag as int
        if flag is set to 1 then it fetches all orders started as of date,
        otherwise (0) it fetches orders, updated as of date"""
        
        ClientMethod.__init__(self, 'GET', '/api/v3/supplier/reportDetailByPeriod', 'stats')
        
        self.dates_fmt = {'date_from': datetime.strptime(date_from, "%Y-%m-%d").strftime("%d-%m-%Y"),
        'date_to': datetime.strptime(date_to, "%Y-%m-%d").strftime("%d-%m-%Y")}
        self.body = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "rrdid": rrdid,
            "limit": limit
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            for _entry in response.json():
                wb_schemas.SupplierFinReport(**_entry)
        except JSONDecodeError as e:
            print('Response content is not a valid json -> ')
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        pass
        # session.prep_req(client_method=self)
        # rrdid: str = '0'
        # page_count: int = 1000

        # while page_count >= 1000:
        #     self.body.update({'rrdid' : rrdid})
        #     time.sleep(2)
        #     with session.get(self.url, params=self.body) as response:
        #         if response.status_code == 200:
        #             self.validate_response(response=response)
        #             if (not response.json()) or (not len(response.json())):
        #                 print(f"This method returned nothing")
        #                 return False
        #             page_count = len(response.json())
        #             rrdid: str = str(response.json()[-1]['rrd_id'])
        #             yield response
        #         else:
        #             print(f"Couldn\'t make it, status code -> {response.status_code} \n \
        #                 with content -> {response.content}")
        #             if response.status_code == 429:
        #                 time.sleep(100)
        #             else:
        #                 break

    def to_file(self, session: ClientSession, output: str) -> None:
        """Saving to a flat file"""
        pass
        # chunks: list = []
        # for chunk in self.get_chunks(session=session):
        #     chunks.append(chunk.json())
        # result: list = list(chain.from_iterable(chunks))
        # file_name = f"wb_financial_{self.dates_fmt['date_from']}_{self.dates_fmt['date_to']}.json"
        
        # try:
        #     with open((output + r'/' + file_name), 'w', encoding='utf-8') as f:
        #         json.dump(result, f)
        #         print("Successfully saved file")
        # except TypeError:
        #     print(f"Error - path - {(output + r'/' + file_name)}")

    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        pass
        # finrep_writer: DBSupplyFinReportUpdater = DBSupplyFinReportUpdater(client_session=session)

        # for chunk in self.get_chunks(session=session):
        #     for finrep_entry in chunk.json():
        #         finrep_model = finrep_writer.prep_model(schema_=wb_schemas.SupplierFinReport(**finrep_entry))
        #         if finrep_writer.check_integrity(finrep_model=finrep_model):
        #             finrep_writer.update(finrep_model)
        #         else:
        #             finrep_writer.create(finrep_model)


class GetV2ListGoodsFilter(ClientMethod):
    def __init__(
        self,
        limit: int = 1000,
        offset: int = 0,
        filter_nm_id: int | None = None
    ) -> None:
        """quantity can take 3 possible flags, 2 - товар с нулевым остатком, 1 - товар с ненулевым остатком,
        0 - товар с любым остатком"""
        
        ClientMethod.__init__(self, 'GET', '/api/v2/list/goods/filter', 'prices')
        
        self.body = {
            "limit": limit,
            "offset": offset,
            "filterNmID": filter_nm_id
        }

    def make_request(self, session : ClientSession) -> Response:
        session.prep_req(client_method=self)

        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            wb_schemas.GetV2ListGoodsFilterResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> Generator[Response, None, None]:
        """
        """
        session.prep_req(client_method=self)
        next_: int = 0
        check_: int = 0

        while not check_:
            # self.params.update({'next': next_})
            self.body['offset'] = next_
            with session.get(self.url, params=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')
            if len(response.json()['data']['listGoods']) >= 1000:
                next_ += 1 * self.body.get('limit')
                continue
            check_ = 1
            
    def process_to_db(self, session: ClientSession) -> None:
        """processes cards into the DB"""
        # pass
        ts_ = datetime.now()
        nomenclature_price_v2_updater: DBNomenclaturePriceV2Updater = DBNomenclaturePriceV2Updater(client_session=session, extraction_ts=ts_)
        for chunk in self.get_chunks(session=session):
            for nomenclature_price_v2_entry in chunk.json()['data']['listGoods']:
                for nomenclature_price_v2_entry_piece in wb_schemas.V2ListGoodsFilterDataGoodsList(**nomenclature_price_v2_entry).to_dict():
                    nomenclature_price_v2_updater.refresh(schema_=nomenclature_price_v2_entry_piece)

