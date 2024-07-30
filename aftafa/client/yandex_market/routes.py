from datetime import datetime, timedelta
import typing as tp
import time

from pydantic import ValidationError
from requests.models import Response

from aftafa.client.yandex_market.crud import DBShopSkuUpdater, DBOrderUpdater, DBOfferPriceUpdater
from aftafa.client.yandex_market.models import session as db_session
import aftafa.client.yandex_market.schemas as ya_schemas
from aftafa.client.yandex_market.client import ClientSession, ClientMethod

from aftafa.utils.helpers import split_into_chunks


class GetCampaigns(ClientMethod):
    def __init__(
        self,
        page: int = 1,
        pageSize: int = 100
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/campaigns')

        self.body = {
            "page": page,
            "pageSize": pageSize
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url, params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.GetCampaignsResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetCampaignsSettings(ClientMethod):
    def __init__(
        self,
        campaign_id: int
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/campaigns/{}/settings')

        self.campaign_id = campaign_id
        self.body = {
            "campaignId": campaign_id
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url.format(str(self.campaign_id)), params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.GetCampaignsSettingsResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetOfferMappings(ClientMethod):
    def __init__(
        self,
        limit: int = 200,
        page_token: str | None = None,
        shop_sku: list[str] = None,
        status: tp.Optional[ya_schemas.ProcessingStateEnum] = None,
        availability: tp.Optional[ya_schemas.OfferAvailabilityStatusType] = None,
        category_id: int = None,
        vendor: str = None
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/campaigns/{}/offer-mapping-entries.json')

        self.body = {
            "limit": limit,
            "page_token": page_token,
            "shop_sku": shop_sku,
            "status": status,
            "availability": availability,
            "category_id": category_id,
            "vendor": vendor
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url.format(session.supplier.id), params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.GetOfferMappingResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> tp.Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        page_token_check: int = 1

        while page_token_check:
            page_token_check = 0
            with session.get(self.url.format(session.supplier.id), params=self.body) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    page_token: tp.Optional[str] = response.json()['result']['paging'].get('nextPageToken', None)
                    if page_token:
                        self.body['page_token'] = page_token
                        page_token_check = 1
                    yield response
                else:
                    print(f"Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                        with content -> {response.content}")


    # def process_to_db(self, session: ClientSession) -> None:
    #     """processes cards into the DB"""
    #     card_updater: DBCardUpdater = DBCardUpdater(client_session=session)

    #     for card_chunk in self.get_chunks(session=session):
    #         if card_chunk:
    #             for card_ in card_chunk.json()['result']['cards']:
    #                 card_updater.process_card(dict_entry=card_)


class PostBusinessOfferMappings(ClientMethod):
    def __init__(
        self,
        limit: int = 200,
        page_token: str | None = None,
        shop_sku: list[str] = None
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/businesses/{}/offer-mappings')

        self.params = {
            "page_token": page_token,
            "limit": limit
        }
        if shop_sku:
            self.body = {
                "offerIds": shop_sku
                # "cardStatuses": [
                #     "HAS_CARD_CAN_NOT_UPDATE"
                # ],
                # "categoryIds": [
                #     0
                # ],
                # "vendorNames": [
                #     "string"
                # ],
                # "tags": [
                #     "string"
                # ],
                # "archived": false
            }
        else:
            self.body = {
            "archived": False
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.post(self.url.format(str(session.supplier.business_id)), json=self.body, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.PostBusinessOfferMappingsResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> tp.Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        
        page_token_check: int = 1

        while page_token_check:
            page_token_check = 0
            with session.post(self.url.format(str(session.supplier.business_id)), json=self.body, params=self.params) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    page_token: tp.Optional[str] = response.json()['result']['paging'].get('nextPageToken', None)
                    if page_token:
                        self.params['page_token'] = page_token
                        page_token_check = 1
                    yield response
                else:
                    print(f"Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                        with content -> {response.content}")


class PostStatsSkus(ClientMethod):
    def __init__(
        self,
        shop_skus: list[str]
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/v2/campaigns/{}/stats/skus.json')

        self.body = {
            "shopSkus": shop_skus
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.post(self.url.format(session.supplier.id), json=self.body) as response:
            if response.status_code == 200:
                # self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.OfferMappingResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes shop skus into the DB"""
        shopsku_updater: DBShopSkuUpdater = DBShopSkuUpdater(client_session=session)
        offer_cont: list[str] = []

        for chunk in GetOfferMappings().get_chunks(session=session):
            for offer_ in chunk.json()['result']['offerMappingEntries']:
                offer_cont.append(offer_['offer']['shopSku'])

        offer_cont = split_into_chunks(offer_cont, 500)

        for offer_cont_part in offer_cont:
            self.body.update(**{'shopSkus': offer_cont_part})
            
            for shop_sku in self.make_request(session=session).json()['result']['shopSkus']:
                shopsku_updater.process_shop_sku(shop_sku=shop_sku)
                shopsku_updater.process_shop_sku_stocks(shop_sku=shop_sku)


class PostStatsSkusV2(ClientMethod):
    def __init__(
        self,
        shop_skus: list[str]
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/campaigns/{}/stats/skus.json')

        self.body = {
            "shopSkus": shop_skus
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.post(self.url.format(session.supplier.id), json=self.body) as response:
            if response.status_code == 200:
                # self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.OfferMappingResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    # def process_to_db(self, session: ClientSession) -> None:
    #     """processes shop skus into the DB"""
    #     shopsku_updater: DBShopSkuUpdater = DBShopSkuUpdater(client_session=session)
    #     offer_cont: list[str] = []

    #     for chunk in GetOfferMappings().get_chunks(session=session):
    #         for offer_ in chunk.json()['result']['offerMappingEntries']:
    #             offer_cont.append(offer_['offer']['shopSku'])

    #     offer_cont = split_into_chunks(offer_cont, 500)

    #     for offer_cont_part in offer_cont:
    #         self.body.update(**{'shopSkus': offer_cont_part})
            
    #         for shop_sku in self.make_request(session=session).json()['result']['shopSkus']:
    #             shopsku_updater.process_shop_sku(shop_sku=shop_sku)
    #             shopsku_updater.process_shop_sku_stocks(shop_sku=shop_sku)
    def process_to_db(self, session: ClientSession) -> None:
        """processes shop skus into the DB"""
        shopsku_updater: DBShopSkuUpdater = DBShopSkuUpdater(client_session=session)
        offer_cont: list[str] = []

        for chunk in PostBusinessOfferMappings().get_chunks(session=session):
            for offer_ in chunk.json()['result']['offerMappings']:
                offer_cont.append(offer_['offer']['offerId'])

        offer_cont = split_into_chunks(offer_cont, 500)

        for offer_cont_part in offer_cont:
            self.body.update(**{'shopSkus': offer_cont_part})
            
            for shop_sku in self.make_request(session=session).json()['result']['shopSkus']:
                shopsku_updater.process_shop_sku(shop_sku=shop_sku)
                shopsku_updater.process_shop_sku_stocks(shop_sku=shop_sku)


class GetOfferPrices(ClientMethod):
    def __init__(
        self,
        campaign_id: int,
        page_token: str | None = None,
        limit: int = 1000
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/campaigns/{}/offer-prices')

        self.campaign_id = campaign_id
        self.body = {
            "page_token": page_token,
            "limit": limit
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url.format(str(self.campaign_id)), params=self.body) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.GetOfferPricesResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes shop skus into the DB"""
        offer_price_updater: DBOfferPriceUpdater = DBOfferPriceUpdater(client_session=session)
        for offer_price_entry in self.make_request(session=session).json()['result']['offers']:
            offer_price_model = offer_price_updater.prep_model(schema_=ya_schemas.OfferPriceResponseDTO(**offer_price_entry))
            if offer_price_updater.check_integrity(offer_price_model=offer_price_model):
                offer_price_updater.update(offer_price_model)
            else:
                offer_price_updater.create(offer_price_model)


class GetWarehouses(ClientMethod):
    def __init__(
        self,
        business_id: int
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/businesses/{}/warehouses')

        self.business_id = business_id
        self.params = {
            "businessId": business_id
        }

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url.format(str(self.business_id)), params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.GetWarehousesResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, session: ClientSession) -> None:
        """processes shop skus into the DB"""
        ...
        # offer_price_updater: DBOfferPriceUpdater = DBOfferPriceUpdater(client_session=session)
        # for offer_price_entry in self.make_request(session=session).json()['result']['offers']:
        #     offer_price_model = offer_price_updater.prep_model(schema_=ya_schemas.OfferPriceResponseDTO(**offer_price_entry))
        #     if offer_price_updater.check_integrity(offer_price_model=offer_price_model):
        #         offer_price_updater.update(offer_price_model)
        #     else:
        #         offer_price_updater.create(offer_price_model)


class PostStatsOrders(ClientMethod):
    def __init__(
        self,
        page_token: str = '',
        limit: int = 200,
        date_from: tp.Optional[str] = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
        date_to: tp.Optional[str] = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d'),
        update_from: tp.Optional[str] = None,
        update_to: tp.Optional[str] = None,
        order_list: list[int] = None,
        status_list: list[str] = None,
        has_cis: bool = None
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/v2/campaigns/{}/stats/orders.json')

        self.body = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "updateFrom": update_from,
                "updateTo": update_to,
                "orders": [
                    order_list
                ],
                "statuses": [
                    status_list
                ],
                "hasCis": has_cis
        }
        self.params = {
            'page_token': page_token,
            'limit': limit
        }

    def make_request(self, session : ClientSession) -> Response:
        self.body = {k: v for k, v in self.body.items() if (v is not None) and (v != [None])}
        with session.post(self.url.format(session.supplier.id), json=self.body, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.OrderResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def get_chunks(self, session: ClientSession) -> tp.Generator[Response, None, None]:
        """gets all the data from API if there is some limit in the method in chunks,
        i.e. returns generator"""
        page_token_check: int = 1
        self.body = {k: v for k, v in self.body.items() if (v is not None) and (v != [None])}

        while page_token_check:
            page_token_check = 0
            with session.post(
                self.url.format(session.supplier.id),
                json=self.body,
                params=self.params
            ) as response:
                if response.status_code == 200:
                    self.validate_response(response=response)
                    if faulty_response := response.json().get('error', None):
                        print(f"This method returned the following error: {faulty_response['message']}")
                        return False
                    page_token: tp.Optional[str] = response.json()['result']['paging'].get('nextPageToken', None)
                    if len(response.json()['result']['orders']) == 200:
                        self.params['page_token'] = page_token
                        page_token_check = 1
                    yield response
                else:
                    print(f"Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                        with content -> {response.content}")

    def process_to_db(self, session: ClientSession) -> None:
        """processes shop skus into the DB"""
        # ...
        order_updater: DBOrderUpdater = DBOrderUpdater(client_session=session)

        for chunk in self.get_chunks(session=session):
            for order_ in chunk.json()['result']['orders']:
                order_updater.refresh(order_schema_=ya_schemas.OrdersStatsOrderDTO(**order_))
                order_updater.populate_order(schema_=ya_schemas.OrdersStatsOrderDTO(**order_))


class PostStocksOnWarehousesGenerate(ClientMethod):
    def __init__(
        self,
        campaign_id: int = 0,
        warehouse_ids: tp.Optional[tp.List[int]] = None
    ) -> None:
        ClientMethod.__init__(self, 'POST', '/reports/stocks-on-warehouses/generate')

        self.body = {
            'campaignId': campaign_id,
            'warehouseIds': warehouse_ids
        }
        self.params = {
            'format': 'FILE'
        }

    def make_request(self, session : ClientSession) -> Response:
        self.body['campaignId'] = int(session.supplier.id)
        with session.post(self.url, json=self.body, params=self.params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                if response.json()['status'] != 'OK':
                    print(f'Couldn\'t make it {response.url}, report status not OK \
                            with content -> {response.content}')
                    return None
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def validate_response(self, response : Response):
        try:
            ya_schemas.PostStocksOnWarehousesGenerateResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


class GetReportsInfo(ClientMethod):
    def __init__(
        self,
        report_id: str
    ) -> None:
        ClientMethod.__init__(self, 'GET', '/reports/info/{}')
        self.report_id = report_id
        self.REPORT_PATH = r'E:\shoptalk\marketplaceapi_\loads\YA\reports\{}'

    def make_request(self, session : ClientSession) -> Response:
        with session.get(self.url.format(self.report_id)) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                if response.json()['status'] != 'OK':
                    print(f'Couldn\'t make it {response.url}, report status not OK \
                            with content -> {response.content}')
                    return None
                return response
            else:
                print(f'Couldn\'t make it {response.url}, status code -> {response.status_code} \n \
                    with content -> {response.content}')

    def get_report(self, session: ClientSession) -> Response:
        i: int = 0

        for i in range(5):
            response = self.make_request(session=session)
            if response.json()['result']['status'] == 'DONE':
                download_url: str = response.json()['result']['file']
                break
            print(f'Report {self.report_id} are not ready yet')
            time.sleep(30)

        with session.get(url=download_url) as file_response:
            with open(self.REPORT_PATH.format((self.report_id + '.xlsx')), 'wb') as f:
                f.write(file_response.content)
                print(f"Successfully saved report {self.report_id}")


    def validate_response(self, response : Response):
        try:
            ya_schemas.GetReportsInfoResponse(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())