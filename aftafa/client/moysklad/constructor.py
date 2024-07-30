import json
from typing import Literal

from requests.models import Response

from aftafa.client.moysklad.handlers import MPsesh
from aftafa.client.moysklad.schemas import Meta, MetaArray, RateMetaArray
from aftafa.client.moysklad.models import (
    EntityAttribute,
    Group,
    session as db_session,
    DocumentState
)


with open(r'E:/shoptalk/marketplaceapi_/scripts/ver_0_2/moysklad_client/mappings.json', "r", encoding='utf-8') as f:
    mappings: dict[str, str] = json.load(f)


class Filler:
    """
    Constructor of meta arrays and hrefs for setting up schemas. Has
    a set of methods for converting an OZON posting into a moysklad
    customer order. For now
    
    Parameters
    ----------
    entity : str
    name : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh

    def construct_metadata(
        self,
        entity: str,
        filter_: Literal['name', 'code', 'isoCode'],
        value: str
    ) -> MetaArray:
        response: Response = self.sesh.make_request(
            'GET', (f'/entity/{entity}?filter={filter_}={value}')
        )
        fetched_meta: Meta = Meta(**response.json()['rows'][0]['meta'])
        if entity == 'currency':
            return RateMetaArray(currency=MetaArray(meta=fetched_meta))
        return MetaArray(meta=fetched_meta)

    def construct_state(self, posting_status: str) -> MetaArray:
        query_filter: bool = DocumentState.name == mappings['ozon_to_ms_states'][posting_status]
        state_id: str = (
            str(db_session.query(DocumentState)
                        .filter(query_filter)
                        .first()
                        .id)
        )
        response: Response = self.sesh.make_request(
            'GET', (f'/entity/customerorder/metadata/states/{state_id}')
        )
        fetched_meta: Meta = Meta(**response.json()['meta'])
        return MetaArray(meta=fetched_meta)

    def construct_group_metadata(self, group_name: str) -> MetaArray:
        query_filter: bool = Group.name == group_name
        group_id: str = (
            str(db_session.query(Group)
                        .filter(query_filter)
                        .first()
                        .id)
        )
        response: Response = self.sesh.make_request(
            'GET', (f'/entity/group/{group_id}')
        )
        fetched_meta: Meta = Meta(**response.json()['meta'])
        return MetaArray(meta=fetched_meta)


class AttrBuilder:
    """
    Constructor of attributes for a given entity. For now
    it is only customerorder, planning on moving it to a
    abstract base class.
    
    Parameters
    ----------
    sesh : MPsesh
    entity : str
    name : str
    """
    def __init__(self, sesh: MPsesh) -> None:
        self.sesh = sesh
        self.filler = Filler(sesh=sesh)
        self.container = []

    def get_attributes_list(self, entity: str = 'customerorder') -> list[str]:
        query_filter: bool = EntityAttribute.entity_type == entity
        attr_list: list[EntityAttribute] = (
            db_session.query(EntityAttribute)
                    .filter(query_filter)
                    .all()
        )
        self.container = attr_list

    def construct_metadata(
        self,
        entity: str,
        filter_: Literal['name', 'code', 'isoCode'],
        value: str
    ) -> MetaArray:
        response: Response = self.sesh.make_request(
            'GET', (f'/entity/{entity}?filter={filter_}={value}')
        )
        fetched_meta: Meta = Meta(**response.json()['rows'][0]['meta'])
        if entity == 'currency':
            return RateMetaArray(currency=MetaArray(meta=fetched_meta))
        return MetaArray(meta=fetched_meta)
