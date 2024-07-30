from datetime import datetime
from typing import Generator, Optional
from requests import Session, Response

from pydantic import ValidationError

from aftafa.client.megamarket.client import ApiClient, BASE_URL
from aftafa.client.megamarket.schemas.catalog import PostCatalogGetListResponse
from aftafa.client.megamarket.schemas.catalog_item import CatalogItem
from aftafa.client.megamarket.schemas.category_list import PostCategoryListResponse, PostCategoryListResponseDataCategoryItem
from aftafa.client.megamarket.schemas.suggest_list import PostSuggestListResponse
from aftafa.client.megamarket.schemas.suggest_list_item import SuggestListItem
from aftafa.client.megamarket.schemas.order_search import OrderSearchItem
from aftafa.client.megamarket.schemas.order_search import PostOrderSearchResponse
from aftafa.client.megamarket.schemas.stock import PostStockGetResponse, StockItem
from aftafa.client.megamarket.schemas.merchant import PostMerchantListResponse, MerchantItem
from aftafa.client.megamarket.crud import (
    DBCatalogUpdater,
    DBCategoryUpdater,
    DBSearchOrderUpdater,
    DBSuggestListUpdater,
    DBMerchantInfoUpdater,
    DBStockUpdater
)


class PostStockGet:
    def __init__(self, session_id: str = '', limit: int = 50, offset: int = 0) -> None:
        self.url = BASE_URL + '/api/market/v3/mcssCore/stock/get'
        self.payload = {
            "meta": {
                "from": "mui-mcs-v2"
            },
            "data": {
                "merchantId": 0,
                "limit": limit,
                "offset": offset,
                "sort":{
                    "field":"quantity",
                    "order":"desc"
                },
                "filter":{
                    "searchText": "",
                    "qualities": [
                        "GENERAL",
                        "DEFECT",
                        "DEFECT_BY_MERCHANT",
                        "DEFECT_BY_RETURN",
                        "DEFECT_BY_OSG",
                        "DEFECT_BY_KM",
                        "DEFECT_BY_STORAGE"
                    ],
                    "facilityIds": [],
                    "amount": None
                },
                "sessionId": session_id
            }
        }
        

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        self.payload['data']['merchantId'] = session._merchant_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            PostStockGetResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        # return
        self.payload['data']['sessionId'] = session.session_id
        self.payload['data']['merchantId'] = session._merchant_id

        check_: int = 0
        i: int = 0
        limit: int = self.payload['data']['limit']

        while not check_:
            self.payload['data']['offset'] = (i * limit)
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    total_count: int = response.json()['data']['total']
                    if total_count <= ((i + 1) * limit):
                        check_ = 1
                    i += 1
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        extraction_ts = datetime.now()
        stock_updater: DBStockUpdater = DBStockUpdater(client_session=session, extraction_ts=extraction_ts)

        for chunk in self.get_chunks(session=session):
            chunk = chunk.json()['data']['items']
            if not chunk:
                return None
            for stock_item in chunk:
                stock_updater.refresh(stock_schema_=StockItem(**stock_item))


class PostMerchantList:
    def __init__(self, session_id: str = '', limit: int = 1000, offset: int = 0) -> None:
        self.url = BASE_URL + '/api/market/v1/partnerService/merchant/search'
        self.payload = {
            'meta': {
                'from': 'mui-header',
            },
            'data': {
                'filter': {},
                'limit': limit,
                'offset': offset,
                'source': 'LKM',
                'sessionId': session_id,
            }
        }

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            PostMerchantListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        pass

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        merchant_info_updater: DBMerchantInfoUpdater = DBMerchantInfoUpdater(client_session=session)
        for merchant_info in self.make_request(session=session).json()['data']['items']:
            merchant_info_updater.refresh(merchant_info_schema_=MerchantItem(**merchant_info))


class PostCatalogGetList():
    def __init__(self, session_id: str = '', limit: int = 120, offset: int = 0) -> None:
        self.url = BASE_URL + '/api/market/v3/partnerService/catalog/getList'
        self.payload = {
            'meta': {
                'from': 'mui-main',
            },
            'data': {
                'filter': {
                    'merchantData': {},
                    'goodsData': {},
                    'publicationStatuses': [],
                },
                'limit': limit,
                'offset': offset,
                'sessionId': session_id,
            }
        }

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            PostCatalogGetListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        # return
        self.payload['data']['sessionId'] = session.session_id

        check_: int = 0
        i: int = 0
        limit: int = self.payload['data']['limit']

        while not check_:
            self.payload['data']['offset'] = (i * limit)
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    total_count: int = response.json()['data']['total']
                    if total_count <= ((i + 1) * limit):
                        check_ = 1
                    i += 1
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        # ...
        main_catalog_item_updater: DBCatalogUpdater = DBCatalogUpdater(client_session=session)
        for chunk in self.get_chunks(session=session):
            for main_catalog_item in chunk.json()['data']['items']:
                try:
                    CatalogItem(**main_catalog_item)
                except ValidationError as e:
                    print(f"This merchant offer id `{main_catalog_item.get('merchantGoods').get('merchantOfferId')}` didn't pass validation, look at it")
                    continue
                main_catalog_item_updater.refresh(main_catalog_item_schema_=CatalogItem(**main_catalog_item))
                main_catalog_item_updater.populate_catalog_item(schema_=CatalogItem(**main_catalog_item))
                
                
class PostSuggestList():
    def __init__(
            self,
            session_id: str = '',
            limit: int = 60,
            offset: int = 0,
            show_available: bool = False,
            show_conflict: bool = False
        ) -> None:
        self.url = BASE_URL + '/api/market/v3/partnerService/suggest/list'
        self.payload = {
            'meta': {
                'from': 'mui-main',
            },
            'data': {
                'filter': {
                    'merchantData': {},
                    'goodsData': {},
                    'publicationStatuses': [],
                    'showAvailable': show_available,
                    'showConflict': show_conflict,
                    'status': 'NoMatch',
                },
                'limit': limit,
                'offset': offset,
                'sessionId': session_id,
            }
        }

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            PostSuggestListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        # return
        self.payload['data']['sessionId'] = session.session_id

        check_: int = 0
        i: int = 0
        limit: int = self.payload['data']['limit']

        while not check_:
            self.payload['data']['offset'] = (i * limit)
            with session.post(self.url, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    total_count: int = response.json()['data']['total']
                    if total_count <= ((i + 1) * limit):
                        check_ = 1
                    i += 1
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        main_catalog_item_updater: DBSuggestListUpdater = DBSuggestListUpdater(client_session=session)
        for chunk in self.get_chunks(session=session):
            for main_catalog_item in chunk.json()['data']['items']:
                try:
                    CatalogItem(**main_catalog_item)
                except ValidationError as e:
                    print(f"This merchant offer id `{main_catalog_item.get('merchantGoods').get('merchantOfferId')}` didn't pass validation, look at it")
                    continue
                main_catalog_item_updater.refresh(main_catalog_item_schema_=SuggestListItem(**main_catalog_item))
                main_catalog_item_updater.populate_catalog_item(schema_=SuggestListItem(**main_catalog_item))


class PostCategoryList():
    def __init__(self, session_id: str = '') -> None:
        self.url = BASE_URL + '/api/market/v3/productService/category/list'
        self.payload = {
            'meta': {
                'from': 'mui-main',
            },
            'data': {
                'sessionId': session_id,
                'status': 'Matched',
            }
        }

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                    

    def validate_response(self, response: Response):
        try:
            PostCategoryListResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        # return None
        category_updater: DBCategoryUpdater = DBCategoryUpdater(client_session=session)
        data = self.make_request(session=session).json()['data']
        if not len(data):
            return None
        
        # if len(data) > 1:
        #     print(f"The category response schema has changed!")
        #     return None
        
        for data_item in data:
            data_item_schema = PostCategoryListResponseDataCategoryItem(**data_item)
            for category_entry in data_item_schema.to_dict():
                category_updater.refresh(category_schema_=category_entry)

        # for chunk in self.get_chunks(session=session):
        #     for main_catalog_item in chunk.json()['data']['items']:
        #         category_updater.refresh(main_catalog_item_schema_=CatalogItem(**main_catalog_item))
        #         category_updater.populate_catalog_item(schema_=CatalogItem(**main_catalog_item))
        
        
class PostOrderSearch():
    def __init__(
        self,
        date_from: datetime,
        date_to: datetime,
        service_schemes: Optional[list[str]] = None,
        fulfillment_method: Optional[list[str]] = None,
        delivery_methods: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 1000,
        is_delete_canceled_items: bool = False,
        session_id: str = ''
    ) -> None:
        self.url = BASE_URL + '/api/merchantUIService/v1/orderService/order/search'
        self.payload = {
            'meta': {
                'from': 'mui-main',
            },
            'data': {
                "isDeleteCanceledItems": is_delete_canceled_items,
                "dateFrom": date_from.strftime("%Y-%m-%dT00:00:00+03:00"),
                "dateTo": date_to.strftime("%Y-%m-%dT23:59:59+03:00"),
                "offset": offset,
                "limit": limit,
                'sessionId': session_id
            }
        }

    def make_request(self, session: Session) -> Response:
        self.payload['data']['sessionId'] = session.session_id
        
        with session.post(self.url, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')
                    

    def validate_response(self, response: Response):
        try:
            PostOrderSearchResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())
            
    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        self.payload['data']['sessionId'] = session.session_id

        check_: int = 0
        i: int = 0
        limit: int = self.payload['data']['limit']

        while not check_:
            self.payload['data']['offset'] = (i * limit)
            with session.post(self.url, json=self.payload) as response:
                if (response.status_code == 200) and (response.json().get('success') == 1):
                    self.validate_response(response=response)
                    yield response
                    total_count: int = response.json()['data']['total']
                    if total_count <= ((i + 1) * limit):
                        check_ = 1
                    i += 1
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        """processes shop skus into the DB"""
        
        order_updater: DBSearchOrderUpdater = DBSearchOrderUpdater(client_session=session)
        for chunk in self.get_chunks(session=session):
            for order in chunk.json()['data']['items']:
                order_updater.refresh(search_order_schema_=OrderSearchItem(**order))
                order_updater.populate_order_items(schema_=OrderSearchItem(**order))
        return None