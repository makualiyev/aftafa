from typing import Literal

from pydantic import BaseModel

from diadoc_client.schema.document import Document
from diadoc_client.schema.entity import Entity
from utils.helpers import to_pascal


class TemplateToLetterTransformationInfo(BaseModel):
    letter_from_box_id: str
    letter_to_box_id: str
    letter_from_department_id: str | None
    letter_to_department_id: str | None
    letter_proxy_box_id: str | None
    letter_proxy_department_id: str | None

    class Config:
        alias_generator = to_pascal


class Message(BaseModel):
    message_id: str
    timestamp_ticks: int
    last_patch_timestamp_ticks: int
    from_box_id: str
    from_title: str
    to_box_id: str | None
    to_title: str | None
    entities: list[Entity | None]
    is_draft: bool | None
    draft_is_locked: bool | None
    draft_is_recycled: bool | None
    created_from_draft_id: str | None
    draft_is_transformed_to_message_id_list: list[str | None]
    is_deleted: bool | None
    is_test: bool | None
    is_internal: bool | None
    is_proxified: bool | None
    proxy_box_id: str | None
    proxy_title: str | None
    packet_is_locked: bool | None
    lock_mode: Literal['None', 'Send', 'Full']
    message_type: Literal['Unknown', 'Letter', 'Draft', 'Template']
    template_to_letter_transformation_info: TemplateToLetterTransformationInfo | None
    is_reusable: bool | None

    class Config:
        alias_generator = to_pascal
