from typing import Literal

from pydantic import BaseModel

from diadoc_client.schema.document import Document
from utils.helpers import to_pascal


class Content(BaseModel):
    Size: int
    Data: bytes | None


class ResolutionInfo(BaseModel):
    ResolutionType: Literal['UndefinedResolutionType','Approve','Disapprove','UnknownResolutionType'] | None
    Author: str
    InitialRequestId: str | None


class ResolutionTarget(BaseModel):
    Department: str | None
    DepartmentId: str | None
    User: str | None
    UserId: str | None


class ResolutionRequestInfo(BaseModel):
    Type: Literal['UnknownResolutionRequestType','ApprovementRequest''SignatureRequest','ApprovementSignatureRequest','Custom'] | None
    Author: str
    Target: ResolutionTarget | None
    ResolvedWith: str | None
    Actions: list[str | None]


class ResolutionRequestDenialInfo(BaseModel):
    Author: str
    InitialRequestId: str | None


class ResolutionRouteAssignmentInfo(BaseModel):
    RouteId: str
    Author: str


class ResolutionRouteRemovalInfo(BaseModel):
    RouteId: str
    Author: str


class CancellationInfo(BaseModel):
    Author: str


class TemplateTransformationInfoDocumentId(BaseModel):
    MessageId: str
    EntityId: str


class TemplateTransformationInfo(BaseModel):
    TransformedToLetterId: TemplateTransformationInfoDocumentId | None
    Author: str | None


class TemplateRefusalInfo(BaseModel):
    Type: Literal['UnknownRefusalType', 'Refusal', 'Withdrawal']
    BoxId: str
    Author: str | None
    Comment: str | None


class OuterDocflowInfoStatusDetail(BaseModel):
    Code: str | None
    Text: str | None


class OuterDocflowInfoStatus(BaseModel):
    NameId: str
    FriendlyName: str
    Type: Literal['UnkownStatus', 'Normal', 'Success', 'Warning', 'Error']
    Description: str | None
    Details: list[OuterDocflowInfoStatusDetail | None]


class OuterDocflowInfo(BaseModel):
    DocflowNamedId: str
    DocflowFriendlyName: str
    Status: OuterDocflowInfoStatus


class SignerDetails(BaseModel):
    Surname: str
    FirstName: str
    Patronymic: str | None
    JobTitle: str | None
    Inn: str
    SoleProprietorRegistrationCertificate: str | None


class Signer(BaseModel):
    SignerCertificate: bytes | None
    SignerDetails: SignerDetails | None
    SignerCertificateThumbprint: str | None



class RevocationRequestInfo(BaseModel):
    Comment: str | None
    Signer: Signer | None


class PowerOfAttorneyFullId(BaseModel):
    RegistrationNumber: str
    IssuerInn: str


class PowerOfAttorneyValidationError(BaseModel):
    Code: str
    Text: str


class RoamingSendingError(BaseModel):
    Code: str
    Text: str


class PowerOfAttorneyValidationStatus(BaseModel):
    Severity: Literal['UnknownSeverity', 'Info', 'Success', 'Warning', 'Error'] | None
    StatusNamedId: Literal['UnknownStatus', 'CanNotBeValidated', 'IsValid', 'IsNotValid', 'ValidationError'] | None
    StatusText: str | None
    Errors: list[PowerOfAttorneyValidationError | None]


class RoamingSendingStatus(BaseModel):
    Severity: Literal['UnknownSeverity', 'Info', 'Success', 'Warning', 'Error'] | None
    StatusNamedId: Literal['UnknownStatus', 'IsSent', 'SendingError'] | None
    StatusText: str
    Errors: list[RoamingSendingError | None]


class PowerOfAttorneyInfo(BaseModel):
    FullId: PowerOfAttorneyFullId
    Status: PowerOfAttorneyValidationStatus | None
    SendingStatus: RoamingSendingStatus | None
    SendingType: Literal['Metadata', 'File', 'DocumentContent'] | None


class MoveDocumentInfo(BaseModel):
    MovedFromDepartment: str
    MovedToDepartment: str


class Entity(BaseModel):
    entity_type: Literal['UnknownEntityType', 'Attachment', 'Signature'] | None
    entity_id: str
    parent_entity_id: str | None
    content: Content | None
    attachment_type: str | None
    file_name: str | None
    need_recipient_signature: bool | None
    signer_box_id: str | None
    not_delivered_event_id: str | None
    document_info = Document
    raw_creation_date: float
    resolution_info: ResolutionInfo | None
    signer_department_id: str | None
    resolution_request_info: ResolutionRequestInfo | None
    resolution_request_denial_info: ResolutionRequestDenialInfo | None
    need_receipt: bool | None
    packet_id: str | None
    is_approvement_signature: bool | None
    is_encrypted_content: bool | None
    attachment_version: str | None
    resolution_route_assignment_info: ResolutionRouteAssignmentInfo | None
    resolution_route_removal_info: ResolutionRouteRemovalInfo | None
    cancellation_info: CancellationInfo | None
    labels: list[str]
    version: str | None
    template_transformation_info: TemplateTransformationInfo | None
    template_refusal_info: TemplateRefusalInfo | None
    outer_docflow_info: OuterDocflowInfo | None
    revocation_request_info: RevocationRequestInfo | None
    content_type_id: str | None
    power_of_attorney_info: PowerOfAttorneyInfo | None
    author_user_id: str | None
    move_document_info: MoveDocumentInfo | None

    class Config:
        alias_generator = to_pascal

    def to_dict(self) -> dict:
        new_repr = self.dict()
        if new_repr['content']:
            new_repr['content_size'] = new_repr['content'].get('Size')
        return new_repr
