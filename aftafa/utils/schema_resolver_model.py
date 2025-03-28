"""
TODO: check this implementation https://github.com/kuimono/openapi-schema-pydantic/
TODO: fix CallbackObject (dynamic variable field names as expressions?)
TODO: SecurityRequirementObject
"""
from typing import Optional, Any

from pydantic import BaseModel, Extra, Field
from pydantic.dataclasses import dataclass


class OpenAPISpecConfig:
    extra = 'allow'


# @dataclass(config=OpenAPISpecConfig)
class ContactObject(BaseModel):
    name: Optional[str]
    url: Optional[str]
    email: Optional[str]


# @dataclass(config=OpenAPISpecConfig)
class LicenseObject(BaseModel):
    name: str
    identifier: Optional[str]
    url: Optional[str]


# @dataclass(config=OpenAPISpecConfig)
class InfoObject(BaseModel):
    title: str
    summary: Optional[str]
    description: Optional[str]
    termsOfService: Optional[str]
    contact: Optional[ContactObject]
    license: Optional[LicenseObject]
    version: str


# @dataclass(config=OpenAPISpecConfig)
class ServerVariableObject(BaseModel):
    enum: list[Optional[str]]
    default: str
    description: Optional[str]


# @dataclass(config=OpenAPISpecConfig)
class ServerObject(BaseModel):
    url: str
    description: Optional[str]
    variables: Optional[dict[str, ServerVariableObject]]


# @dataclass(config=OpenAPISpecConfig)
class ExternalDocumentationObject(BaseModel):
    description: Optional[str]
    url: str


# @dataclass(config=OpenAPISpecConfig)
class ParameterObject(BaseModel):
    name: str
    description: Optional[str]
    required: Optional[bool]
    deprecated: Optional[bool]
    allowEmptyValue: Optional[bool]
    in_: str = Field(alias='in')


# @dataclass(config=OpenAPISpecConfig)
class ReferenceObject(BaseModel):
    ref: str = Field(alias="$ref")
    summary: Optional[str]
    description: Optional[str]


# @dataclass(config=OpenAPISpecConfig)
class HeaderObject(BaseModel):
    name: str
    description: str
    required: Optional[bool]
    deprecated: bool
    allowEmptyValue: Optional[bool]
    in_: str = Field(alias='in')


# @dataclass(config=OpenAPISpecConfig)
class EncodingObject(BaseModel):
    contentType: Optional[str]
    headers: dict[str, HeaderObject | ReferenceObject]
    style: Optional[str]
    explode: Optional[bool]
    allowReserved: Optional[bool]


# @dataclass(config=OpenAPISpecConfig)
class DiscriminatorObject(BaseModel):
    propertyName: str
    mapping: dict[str, str]


# @dataclass(config=OpenAPISpecConfig)
class XMLObject(BaseModel):
    name: str
    namespace: str
    prefix: str
    attribute: bool
    wrapped: bool


# @dataclass(config=OpenAPISpecConfig)
class SchemaObject(BaseModel):
    discriminator: Optional[DiscriminatorObject]
    xml: Optional[XMLObject]
    externalDocs: Optional[ExternalDocumentationObject]
    example: Optional[Any]


# @dataclass(config=OpenAPISpecConfig)
class ExampleObject(BaseModel):
    summary: Optional[str]
    description: Optional[str]
    value: Any
    externalValue: Optional[str]


# @dataclass(config=OpenAPISpecConfig)
class MediaTypeObject(BaseModel):
    media_type_schema: Optional[SchemaObject | ReferenceObject] = Field(alias='schema')
    example: Optional[Any]
    examples: Optional[dict[str, ExampleObject | ReferenceObject]]
    encoding: Optional[dict[str, EncodingObject]]


# @dataclass(config=OpenAPISpecConfig)
class RequestBodyObject(BaseModel):
    description: Optional[str]
    content: dict[str, MediaTypeObject]
    required: Optional[bool]


# @dataclass(config=OpenAPISpecConfig)
class LinkObject(BaseModel):
    operationRef: str
    operationId: str
    parameters: Optional[dict[str, Any | str]]
    requestBody: Optional[Any | str]
    description: Optional[str]
    server: Optional[ServerObject]


# @dataclass(config=OpenAPISpecConfig)
class ResponseObject(BaseModel):
    description: str
    headers: Optional[dict[str, HeaderObject | ReferenceObject]]
    content: Optional[dict[str, MediaTypeObject]]
    links: Optional[dict[str, LinkObject | ReferenceObject]]


# @dataclass(config=OpenAPISpecConfig)
class ResponsesObject(BaseModel, extra=Extra.forbid):
    default: Optional[ResponseObject | ReferenceObject]
    status_code_200: Optional[ResponseObject | ReferenceObject] = Field(alias='200')
    status_code_201: Optional[ResponseObject | ReferenceObject] = Field(alias='201')
    status_code_204: Optional[ResponseObject | ReferenceObject] = Field(alias='204')
    status_code_208: Optional[ResponseObject | ReferenceObject] = Field(alias='208')
    status_code_209: Optional[ResponseObject | ReferenceObject] = Field(alias='209')
    status_code_400: Optional[ResponseObject | ReferenceObject] = Field(alias='400')
    status_code_401: Optional[ResponseObject | ReferenceObject] = Field(alias='401')
    status_code_403: Optional[ResponseObject | ReferenceObject] = Field(alias='403')
    status_code_404: Optional[ResponseObject | ReferenceObject] = Field(alias='404')
    status_code_406: Optional[ResponseObject | ReferenceObject] = Field(alias='406')
    status_code_409: Optional[ResponseObject | ReferenceObject] = Field(alias='409')
    status_code_413: Optional[ResponseObject | ReferenceObject] = Field(alias='413')
    status_code_422: Optional[ResponseObject | ReferenceObject] = Field(alias='422')
    status_code_429: Optional[ResponseObject | ReferenceObject] = Field(alias='429')
    status_code_500: Optional[ResponseObject | ReferenceObject] = Field(alias='500')

    

# @dataclass(config=OpenAPISpecConfig)
class TagObject(BaseModel):
    name: str
    description: Optional[str]
    externalDocs: Optional[ExternalDocumentationObject]


# @dataclass(config=OpenAPISpecConfig)
class SecurityRequirementObject(BaseModel):
    name: str


# @dataclass(config=OpenAPISpecConfig)
class OAuthFlowObject(BaseModel):
    authorizationUrl: str
    tokenUrl: str
    refreshUrl: Optional[str]
    scopes: dict[str, str]


# @dataclass(config=OpenAPISpecConfig)
class OAuthFlowsObject(BaseModel):
    implicit: Optional[OAuthFlowObject]
    password: Optional[OAuthFlowObject]
    clientCredentials: Optional[OAuthFlowObject]
    authorizationCode: Optional[OAuthFlowObject]



# @dataclass(config=OpenAPISpecConfig)
class SecuritySchemeObject(BaseModel):
    security_scheme_type: str = Field(alias='type')         # /Literal["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"]
    description: Optional[str]
    name: str
    scheme: Optional[str]                                   # FIXME: actually not optional, but REQUIRED
    bearerForamt: Optional[str]
    flows: Optional[OAuthFlowsObject]                       # FIXME: actually not optional, but REQUIRED
    openIdConnectUrl: Optional[str]                         # FIXME: actually not optional, but REQUIRED
    in_: str = Field(alias='in')



# @dataclass(config=OpenAPISpecConfig)
class OperationObject(BaseModel):
    tags: Optional[list[str]]
    summary: Optional[str]
    description: Optional[str]
    externalDocs: Optional[ExternalDocumentationObject]
    operationId: Optional[str]
    parameters: Optional[list[ParameterObject | ReferenceObject]]
    requestBody: Optional[RequestBodyObject | ReferenceObject]
    responses: ResponsesObject
    callbacks: Optional[dict[str, ReferenceObject]]                     # FIXME: CallbackObject
    deprecated: Optional[bool]
    security: Optional[list[dict[str, list[Optional[str]]]]]                       # FIXME: SecurityRequirementObject
    servers: Optional[list[ServerObject]]



# @dataclass(config=OpenAPISpecConfig)
class PathItemObject(BaseModel):
    ref: Optional[str] = Field(alias='$ref')
    summary: Optional[str]
    description: Optional[str]
    get: Optional[OperationObject]
    put: Optional[OperationObject]
    post: Optional[OperationObject]
    delete: Optional[OperationObject]
    options: Optional[OperationObject]
    head: Optional[OperationObject]
    patch: Optional[OperationObject]
    trace: Optional[OperationObject]
    servers: Optional[list[ServerObject]]
    parameters: Optional[list[ParameterObject | ReferenceObject]]


# @dataclass(config=OpenAPISpecConfig)
class CallbackObject(BaseModel):
    expression: PathItemObject | ReferenceObject


# @dataclass(config=OpenAPISpecConfig)
class ComponentsObject(BaseModel):
    schemas: Optional[dict[str, SchemaObject]]
    responses: Optional[dict[str, ResponseObject | ReferenceObject]]
    parameters: Optional[dict[str, ParameterObject | ReferenceObject]]
    examples: Optional[dict[str, ExampleObject | ReferenceObject]]
    requestBodies: Optional[dict[str, RequestBodyObject | ReferenceObject]]
    headers: Optional[dict[str, HeaderObject | ReferenceObject]]
    securitySchemes: Optional[dict[str, SecuritySchemeObject | ReferenceObject]]
    links: Optional[dict[str, LinkObject | ReferenceObject]]
    callbacks: Optional[dict[str, CallbackObject | ReferenceObject]]
    pathItems: Optional[dict[str, PathItemObject | ReferenceObject]]


# @dataclass(config=OpenAPISpecConfig)
class OpenAPISpec(BaseModel):
    openapi: str
    info: InfoObject
    jsonSchemaDialect: Optional[str]
    servers: Optional[list[Optional[ServerObject]]]
    paths: Optional[dict[str, PathItemObject]]
    webhooks: Optional[dict[str, PathItemObject | ReferenceObject]]
    components: Optional[ComponentsObject]
    # security: Optional[list[SecurityRequirementObject]]
    security: Optional[list[dict[str, list[Optional[str]]]]]
    tags: Optional[list[TagObject]]
    externalDocs: Optional[ExternalDocumentationObject]
