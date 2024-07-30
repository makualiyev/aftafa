from typing import Generator
from datetime import datetime
from requests import Session, Response

from pydantic import ValidationError

from aftafa.client.mvideo.client import BASE_URL
import aftafa.client.mvideo.schemas as schemas
from aftafa.client.mvideo.models import (
    session as db_session,
    Order
)
from aftafa.client.mvideo.crud import (
    ProductDBWriter,
    ProductPriceDBWriter,
    ProductMovementDBWriter,
    OrderDBWriter,
    OrderEntryDBWriter
)
from aftafa.utils.helpers import bcolors


class GetCatalog():
    def __init__(self, page: int = 0, size: int = 100, filter_: str = "archived:false,productType:MARKETPLACE", fields_: str = "+prices") -> None:
        self.url = BASE_URL + '/api/catalog'
        self.params = {
            "page" : page,
            "size" : size,
            "sort" : "createdDate,desc",
            "filter" : filter_,                                             # lifeCycleStatus:VALIDATION_PASSED|PUBLISHED, --- add this to filter by statuses
            "fields" : fields_
        }

    def make_request(self, session: Session) -> Response:
        with session.get(self.url, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            schemas.GetCatalogResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        check_: int = 0
        i: int = 0

        while not check_:
            self.params.update({'page': i})
            with session.get(self.url, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    page_count: int = response.json()['pages']
                    i += 1
                    if i >= page_count:
                        check_ = 1
                    
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def get_products(self, session: Session) -> None:
        def process_entry(product_entry: dict) -> tuple[bool]:
            """
            
            """
            product_writer = ProductDBWriter()
            price_writer = ProductPriceDBWriter()
            prod_model = product_writer.prep_model(schema_=schemas.GetCatalogResponseContentElement(**product_entry))
            prod_present_in_db: bool = product_writer.check_integrity(product_model=prod_model)
            price_entry_present: bool = False
            prod_price_present_in_db: bool = False

            if price_entry := product_entry.get('prices', None):
                if price_entry.get('currentPrice', None):
                    price_entry_present = True
            if price_entry_present:
                prod_price_model = price_writer.prep_model(schema_=schemas.GetCatalogResponseContentElementPricesPriceEntry(**product_['prices']['currentPrice']))
                prod_price_present_in_db = price_writer.check_integrity(product_model=prod_price_model)

            if prod_present_in_db:
                product_writer.update(prod_model)
            else:
                product_writer.create(prod_model)

            if price_entry_present:
                if prod_price_present_in_db:
                    price_writer.update(prod_price_model)
                else:
                    price_writer.create(prod_price_model)
            


        for chunk_ in self.get_chunks(session=session):
            for product_ in chunk_.json()['content']:
                process_entry(product_entry=product_)

        print(bcolors.OKGREEN + f'Processed catalog for {session.supplier} successfully!' + bcolors.ENDC)


class GetOrders():
    def __init__(self,  supplier_code: str, page: int = 1, size: int = 100, filter: str = '') -> None:
        self.url = BASE_URL + '/api/order/search'
        self.supplier_code = supplier_code
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*'
        }
        self.payload = {
            "filters" : [],            # lifeCycleStatus:VALIDATION_PASSED|PUBLISHED, --- add this to filter by statuses
            "pageable": {
                "page": page,
                "size": size,
                "sorts": [
                    {
                        "field": "dateCreate",
                        "sortType": "DESC"
                    }
                ]
            }
        }

    def make_request(self, session: Session) -> Response:
        with session.post(self.url, headers=self.headers, json=self.payload) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            schemas.GetOrdersResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        check_: int = 0
        i: int = 1

        while not check_:
            self.payload['pageable']['page'] = i
            with session.post(self.url, headers=self.headers, json=self.payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    page_count: int = response.json()['count']
                    i += 1
                    if i > page_count:
                        check_ = 1
                    
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        order_writer = OrderDBWriter(supplier_code=session.supplier['code'])

        for chunk_ in self.get_chunks(session=session):
            for order_entry in chunk_.json()['content']:
                order_model = order_writer.prep_model(schema_=schemas.GetOrdersResponseContentElement(**order_entry))
                if order_writer.check_integrity(order_model=order_model):
                    order_writer.update(order_model)
                else:
                    order_writer.create(order_model)
        
        print(bcolors.OKGREEN + f'Processed orders for {session.supplier} successfully!' + bcolors.ENDC)


class GetOrderEntries():
    def __init__(self, order_number: str, page: int = 1, size: int = 100) -> None:
        self.order_number = order_number
        self.url = BASE_URL + '/api/order/entries/search'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*'
        }
        self.payload = lambda consignment_number: {
            "pageable":{
                "page":page,
                "size":size,
                "sorts":[
                    {
                        "field":"materialSupplierCode",
                        "sortType":"DESC"
                    }
                ]
            },
            "filters":[
                {
                    "operationType":"IN",
                    "values":[
                        consignment_number
                    ],
                    "fieldName":"consignment",
                    "predicatType":"AND"
                }
            ]
        }

    def get_order_consignment(self, session: Session) -> str:
        order_queried =  db_session.query(Order).filter(
                            Order.order_number == self.order_number,
                            Order.supplier_code == session.supplier['code']
                        ).first()
        return order_queried.consignment

    def make_request(self, session: Session) -> Response:
        with session.post(self.url, headers=self.headers, json=self.payload(consignment_number=self.get_order_consignment(session=session))) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            schemas.GetOrderEntriesResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        check_: int = 0
        i: int = 1
        payload = self.payload(consignment_number=self.get_order_consignment(session=session))

        while not check_:
            payload['pageable']['page'] = i
            with session.post(self.url, headers=self.headers, json=payload) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    page_count: int = response.json()['count']
                    i += 1
                    if i > page_count:
                        check_ = 1
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session, extraction_ts: datetime | None = None) -> None:
        order_entry_writer = OrderEntryDBWriter(order_number=self.order_number, extraction_ts=extraction_ts)

        for chunk_ in self.get_chunks(session=session):
            for order_entry in chunk_.json()['content']:
                order_entry_model = order_entry_writer.prep_model(schema_=schemas.GetOrderEntriesResponseContentElement(**order_entry))
                if order_entry_writer.check_integrity(order_entry_model=order_entry_model):
                    order_entry_writer.update(order_entry_model)
                else:
                    order_entry_writer.create(order_entry_model)


class GetProductMovements():
    def __init__(self, page: int = 1, size: int = 100, filter_: str = 'productType:MARKETPLACE') -> None:
        self.url = BASE_URL + '/api/productmovements/search'
        self.params = {
            "page" : page,
            "pageSize" : size,
            "filter" : filter_            # parentUid:NULL
        }

    def make_request(self, session: Session) -> Response:
        with session.get(self.url, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response: Response):
        try:
            schemas.GetProductMovementsResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: Session) -> Generator[Response, None, None]:
        check_: int = 0
        i: int = 1

        while not check_:
            self.params.update({'page': i})
            with session.get(self.url, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    yield response
                    page_count: int = response.json()['pages']
                    i += 1
                    if i > page_count:
                        check_ = 1
                    
                else:
                    print(f'Couldn\'t make it, status code -> {response.status_code} \n \
                        with content -> {response.content}')

    def process_to_db(self, session: Session) -> None:
        product_movement_writer = ProductMovementDBWriter()

        for chunk_ in self.get_chunks(session=session):
            for product_movement_entry in chunk_.json()['content']:
                product_movement_model = product_movement_writer.prep_model(schema_=schemas.GetProductMovementsResponseContentElement(**product_movement_entry))
                if product_movement_writer.check_integrity(product_movement_model=product_movement_model):
                    product_movement_writer.update(product_movement_model)
                else:
                    product_movement_writer.create(product_movement_model)

        print(bcolors.OKGREEN + f'Processed product movements for {session.supplier} successfully!' + bcolors.ENDC)