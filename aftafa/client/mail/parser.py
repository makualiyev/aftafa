"""email message parser based on email.message.Message class.
Just convenience methods for using in pipeline.
"""
from typing import Generator

from dataclasses import dataclass
from datetime import datetime
import email
import mimetypes

from aftafa.utils.helpers import generate_random_hash


@dataclass
class EmailAttachment:
    email_uid: str
    attachment_uid: str
    email_mailbox: str
    email_timestamp: datetime
    email_from: str
    email_subject: str
    email_content_type: str
    email_is_multipart: str
    mimetype: str
    content_dispositon: str | None
    content_transfer_encoding: str | None
    filename: str
    decoded_filename: str | None
    decoded_file_extension: str | None
    data: str | None


class EmailParser:
    def __init__(self, ctx: email.message.Message | dict[str, str | bytes]) -> None:
        self.uid: str = generate_random_hash(n=5)
        self.ctx_meta: dict[str, str | int] | None = None
        if not isinstance(ctx, email.message.Message):
            self.ctx_meta = ctx.get('metadata')
            ctx = email.message_from_bytes(ctx.get('data'))
        self.ctx = ctx
        self.email_timestamp: datetime = email.utils.parsedate_to_datetime(ctx.get('Date'))
        self.email_from: dict[str, str] = self._get_from(item=ctx.get('From'))
        self.email_subject: str = self._get_subject(item=ctx.get('Subject'))
        self.email_content_type: str = ctx.get_content_type()
        self.email_is_multipart: bool = ctx.is_multipart()
        self.payloads: list[email.message.Message | None] = self._extract_payloads(self.ctx)
        self.attachments: list[EmailAttachment | None] = self._extract_attachments()

    def _get_from(self, item: str) -> dict[str, str]:
        parsed_address: tuple[str] = email.utils.parseaddr(item)
        decoded_ctx_str: str = ""
        if parsed_address[0]:
            if parsed_address[0].startswith('='):
                decoded_ctx = email.header.decode_header(parsed_address[0])
                decoded_ctx_str = decoded_ctx[0][0].decode(decoded_ctx[0][1])
            else:
                decoded_ctx_str = parsed_address[0]
        return {
            'from_string': decoded_ctx_str,
            'from_address': parsed_address[1]
        }

    def _get_subject(self, item: str) -> dict[str, str]:
        decoded_ctx: list[tuple[bytes, str]] = email.header.decode_header(item)
        decoded_ctx_str: str = ""
        
        try:
            assert len(decoded_ctx) == 1, "items -> Subject -> decoded subject doesn't give us a list of one element!"
        except AssertionError as ass_err:
            print(ass_err)
        
        decoded_ctx: tuple[bytes, str] = decoded_ctx[0]
        decoded_ctx_str = decoded_ctx[0].decode(decoded_ctx[1])
        
        return decoded_ctx_str
    
    def _extract_payloads(self, ctx: email.message.Message) -> Generator[email.message.Message, None, None]:
        for payload in ctx.get_payload():
            if isinstance(payload.get_payload(), list):
                yield from self._extract_payloads(payload)
            yield payload

    def _extract_attachments(self) -> Generator[email.message.Message, None, None]:
        if self.ctx_meta:
            message_uid: str = str(self.ctx_meta.get('uid'))
            mailbox: str = str(self.ctx_meta.get('mailbox'))
        else:
            message_uid: str = '0'
            mailbox: str = ''

        for payload in self.payloads:
            payload_type: str = payload.get_content_type()
            payload_filename: str = payload.get_filename()
            decoded_ctx_str: str | None = None
            content_disposition: str | None = payload.get_content_disposition()
            if content_disposition and (content_disposition.count('?') > 1):
                content_disposition = None
            decoded_file_extension: str | None = None
            if payload_filename:
                decoded_ctx: list[tuple[bytes, str]] = email.header.decode_header(payload_filename)[0]
                if isinstance(decoded_ctx[0], str):
                    decoded_ctx_str = decoded_ctx[0]
                else:
                    decoded_ctx_str = decoded_ctx[0].decode(decoded_ctx[1])
                decoded_file_extension: str = decoded_ctx_str.split('.')[-1]

            attachment = EmailAttachment(
                email_uid='-'.join([
                    message_uid,
                    self.uid
                ]),
                attachment_uid='-'.join([
                    message_uid,
                    self.uid,
                    generate_random_hash(n=5)
                ]),
                email_mailbox=mailbox,
                email_timestamp=self.email_timestamp,
                email_from=self.email_from.get('from_address'),
                email_subject=self.email_subject,
                email_content_type=self.email_content_type,
                email_is_multipart=self.email_is_multipart,
                mimetype=payload_type,
                content_dispositon=content_disposition,
                content_transfer_encoding=payload.get('Content-Transfer-Encoding'),
                filename=payload.get_filename(),
                decoded_filename=decoded_ctx_str,
                decoded_file_extension=decoded_file_extension,
                data=payload.get_payload()
            )
            yield attachment


    