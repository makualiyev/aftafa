import time
from typing import Generator
from datetime import datetime
from pathlib import Path

from requests import Response
from pydantic import ValidationError

from aftafa.client.diadoc.client import BASE_URL, DiadocClient
from aftafa.client.diadoc.schema.document import GetDocumentsResponse as GetDocumentsResponseSchema, Document as DocumentSchema
from aftafa.client.diadoc.schema.message import Message as GetV5MessageSchema
from aftafa.client.diadoc.crud import DBDocumentUpdater, DBMessageUpdater, DBEntityContentUpdater
from aftafa.utils.helpers import bcolors


class DiadocResource:
    def __init__(self, method: str, path: str) -> None:
        self.method = method
        self.path = path
        self.url = BASE_URL + self.path


class GetCounteragents(DiadocResource):
    def __init__(self, my_org_id: str = None) -> None:
        if my_org_id:
            self.my_org_id = my_org_id
        else:
            self.my_org_id = '28a5fd24-826c-4180-a896-e5d965ff4ddb'
        super().__init__('GET', 'V2/GetCounteragents')

        
    def make_request(self, client: DiadocClient) -> Response:
        with client.get(
            url=self.url,
            params={
                'myOrgId': self.my_org_id
            }
        ) as response:
            if response.status_code == 200:
                return response
            else:
                print(f"Failed this [{self.path}] request -> {response.status_code}")
                return response
            

    def get_sklad_a_box(self, client: DiadocClient) -> dict[str, str]:
        response = self.make_request(client=client)
        try:
            assert len([counteragent for counteragent in response.json()['Counteragents'] if 'Общество с ограниченной ответственностью "Склад А"' in counteragent['Organization']['FullName']]) == 1, "Something's fucked up with getting right counteragent 'Sklad A' org id"
            assert len([counteragent for counteragent in response.json()['Counteragents'] if 'Общество с ограниченной ответственностью "Склад А"' in counteragent['Organization']['FullName']][0]['Organization']['Boxes']) == 1, "Something's fucked up with getting right counteragent 'Sklad A' box id"
        except AssertionError as e:
            print(e)

        counteragent_entry = [counteragent for counteragent in response.json()['Counteragents'] if 'Общество с ограниченной ответственностью "Склад А"' in counteragent['Organization']['FullName']][0]

        org_id = counteragent_entry['Organization']['OrgId']
        box_id = counteragent_entry['Organization']['Boxes'][0]['BoxId']
        return {
            'org_id': org_id,
            'box_id': box_id
        }
            

class GetDocuments(DiadocResource):
    def __init__(self) -> None:
        super().__init__('GET', 'V3/GetDocuments')
        self._params = {
                    'boxId': '4284b03c9a5148a5b164cd38a0471998@diadoc.ru',
                    'filterCategory': 'Any.InboundNotRevoked',
                    'counteragentBoxId': '',
                    'fromDocumentDate': ''
        }

    def make_request(
            self,
            client: DiadocClient,
            box_id: str = '6817822838e145068b2f26528c461a7b@diadoc.ru',
            date_from: str = datetime.now().strftime('%d.%m.%Y')
                ) -> Response:
        params = self._params.copy()
        params['counteragentBoxId'] = box_id
        params['fromDocumentDate'] = date_from

        with client.get(url=self.url, params=params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Failed this [{self.path}] request -> {response.status_code}")
                return response
    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            GetDocumentsResponseSchema(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())


    def get_chunks(self, client: DiadocClient, box_id: str = '6817822838e145068b2f26528c461a7b@diadoc.ru', date_from: str = datetime.now().strftime('%d.%m.%Y')) -> Generator[Response, None, None]:
        def split_into_chunks(total : int, n_size : int) -> int:
            """Used to split product ids into small chunks of a size 100"""
            return (total // n_size) + 1 if (total % n_size) > 0 else total // n_size
        
        params = self._params.copy()
        params['counteragentBoxId'] = box_id
        params['fromDocumentDate'] = date_from

        check: int = 0
        counter: int = 1
        total_count: int = 1
        has_more_results: bool = True
        
        while has_more_results:
            while total_count:
                with client.get(url=self.url, params=params) as response:
                    if response.status_code == 200:
                        self.validate_response(response=response)
                        yield response

                        if counter == 1:
                            total_count = split_into_chunks(response.json()['TotalCount'], 100)
                            has_more_results = response.json()['HasMoreResults']

                        total_count -= 1
                        counter += 1
                        params['afterIndexKey'] = response.json()['Documents'][-1]['IndexKey']
                    elif response.status_code == 429:
                        time.sleep(30)
                        continue
                    else:
                        print(f"Failed this [{self.path}] request -> {response.status_code}")
                        break

            if has_more_results:
                params['afterIndexKey'] = response.json()['Documents'][-1]['IndexKey']
                total_count = 1
                counter = 1

    def process_to_db(self, client: DiadocClient, box_id: str = '6817822838e145068b2f26528c461a7b@diadoc.ru', date_from: str = datetime.now().strftime('%d.%m.%Y')) -> None:
        extraction_ts = datetime.now()
        doc_updater: DBDocumentUpdater = DBDocumentUpdater(client_session=client, extraction_ts=extraction_ts)
        for chunk in GetDocuments().get_chunks(client, box_id=box_id, date_from=date_from):
            for doc in chunk.json()['Documents']:
                doc_updater.refresh(document_schema=DocumentSchema(**doc))

        print(bcolors.OKGREEN + f"Successfully rendered documents from this date {date_from} !" + bcolors.ENDC)

                
            
            
            

class GetV5Message(DiadocResource):
    def __init__(self) -> None:
        super().__init__('GET', 'V5/GetMessage')
        self._params = {
                    'boxId': '4284b03c9a5148a5b164cd38a0471998@diadoc.ru',
                    'messageId': ''
        }

    def make_request(self, client: DiadocClient, message_id: str, entity_id: str | None = None) -> Response:
        params = self._params.copy()
        params['messageId'] = message_id
        if entity_id:
            params['entityId'] = entity_id

        with client.get(url=self.url, params=params) as response:
            if response.status_code == 200:
                self.validate_response(response=response)
                return response
            else:
                print(f"Failed this [{self.path}] request -> {response.status_code}")
                return response
    
    def validate_response(self, response : Response):
        """ fill this"""
        try:
            GetV5MessageSchema(**response.json())
        except ValidationError as e:
            print('Validation failed ->', e.json())

    def process_to_db(self, client: DiadocClient, date_from: str = None) -> None:
        extraction_ts = datetime.now()
        msg_updater: DBMessageUpdater = DBMessageUpdater(client_session=client, extraction_ts=extraction_ts)
        message_ids = msg_updater.get_message_ids(date_from=date_from)
        if message_ids:
            for message_id in message_ids:
                response = self.make_request(client=client, message_id=message_id)
                msg_updater.refresh(message_schema=GetV5MessageSchema(**response.json()))


        
        print(bcolors.OKGREEN + f"Successfully rendered messages from this date {date_from} in database!" + bcolors.ENDC)
    
            

class GetV4EntityContent(DiadocResource):
    def __init__(self) -> None:
        super().__init__('GET', 'V4/GetEntityContent')
        self._params = {
                    'boxId': '4284b03c9a5148a5b164cd38a0471998@diadoc.ru',
                    'messageId': '',
                    'entityId': ''
        }

    def make_request(self, client: DiadocClient, message_id: str, entity_id: str) -> Response:
        params = self._params.copy()
        params['messageId'] = message_id
        params['entityId'] = entity_id

        with client.get(url=self.url, params=params) as response:
            if response.status_code == 200:
                return response
            else:
                print(f"Failed this [{self.path}] request -> {response.status_code}")
                return response
    
    def save_to_file(self, response : Response, path: str):
        path = Path(path)
        if not path.is_dir():
            print(f"Provided incorrect path to file -> {path}")
            return False
        
        with open(path, 'wb') as f:
            f.write(response.content)
            print(f"Successfully saved -> {path.stem}")


    def process_to_db(self, client: DiadocClient, file_destination: str, date_from: str = None) -> None:
        extraction_ts = datetime.now()
        entity_updater: DBEntityContentUpdater = DBEntityContentUpdater(
            client_session=client,
            file_destination=file_destination,
            extraction_ts=extraction_ts
        )
        entity_ids = entity_updater.get_entities_for_content(date_from=date_from)

        if not entity_ids:
            return None

        for entity_id_entry in entity_ids:
            response = self.make_request(client=client, message_id=entity_id_entry.get('message_id'), entity_id=entity_id_entry.get('entity_id'))
            entity_updater.save_to_file(response=response, entity_entry=entity_id_entry)

        
        print(bcolors.OKGREEN + f"Successfully rendered entity contents from this date {date_from} in database!" + bcolors.ENDC)


