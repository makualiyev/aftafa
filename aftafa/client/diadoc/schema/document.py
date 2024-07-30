from pydantic import BaseModel, ConfigDict

from utils.helpers import to_camel, to_pascal


class DocumentContentField(BaseModel):
    Size: int


class DocumentNormalizedDocumentMetadataField(BaseModel):
    DocumentStatus: str
    ReceiptStatus: str

class DocumentMetadataField(BaseModel):
    Key: str
    Value: str


class ConfirmationMetadata(BaseModel):
    ReceiptStatus: str
    DateTimeTicks: int



class RecipientReceiptMetadataField(BaseModel):
    ReceiptStatus: str
    ConfirmationMetadata: ConfirmationMetadata


class AmendmentRequestMetadataField(BaseModel):
    AmendmentFlags: int
    ReceiptStatus: str


class SenderReceiptMetadataField(BaseModel):
    ReceiptStatus: str
    
    
    
class DocflowStatusFieldPrimaryStatusField(BaseModel):
    Severity: str
    StatusText: str


class DocflowStatusField(BaseModel):
    PrimaryStatus: DocflowStatusFieldPrimaryStatusField


class Document(BaseModel):
    index_key: str
    message_id: str
    entity_id: str
    creation_timestamp_ticks: float
    counteragent_box_id: str
    document_type: str
    initial_document_ids: list[None | str]
    subordinate_document_ids: list[None | str]
    content: DocumentContentField
    file_name: str
    document_date: str
    document_number: str
    nonformalized_document_metadata: DocumentNormalizedDocumentMetadataField | None
    is_deleted: bool
    department_id: str
    is_test: bool
    from_department_id: str
    to_department_id: str
    revocation_status: str
    send_timestamp_ticks: int
    delivery_timestamp_ticks: int
    forward_document_events: list[None | str]
    roaming_notification_status: str
    has_custom_print_form: bool
    custom_data: list[None | str]
    document_direction: str
    last_modification_timestamp_ticks: int
    is_encrypted_content: bool
    sender_signature_status: str
    is_read: bool
    packet_is_locked: bool
    proxy_signature_status: str
    type_named_id: str
    function: str
    workflow_id: int
    title: str
    metadata: list[None | DocumentMetadataField]
    recipient_receipt_metadata: RecipientReceiptMetadataField
    confirmation_metadata: ConfirmationMetadata
    recipient_response_status: str
    amendment_request_metadata: AmendmentRequestMetadataField
    editing_setting_id: str
    lock_mode: str
    sender_receipt_metadata: SenderReceiptMetadataField
    version: str
    last_outer_docflows: list[None | str]
    docflow_status: DocflowStatusField
    message_id_guid: str
    entity_id_guid: str
    creation_timestamp: str

    class Config:
        alias_generator = to_pascal


class GetDocumentsResponse(BaseModel):
    total_count: int
    documents: list[Document | None]
    has_more_results: bool

    class Config:
        alias_generator = to_pascal
