"""email message parser based on email.message.Message class.
Just convenience methods for using in pipeline.
"""
from typing import Generator

import email


class EmailParser:
    def __init__(self, ctx: email.message.Message) -> None:
        self.ctx = ctx
        self.email_from: dict[str, str] = self._get_from(item=ctx.get('From'))
        self.email_subject: str = self._get_subject(item=ctx.get('Subject'))
        self.email_content_type: str = self.get_content_type()
        self._init_parser()

    def _init_parser(self) -> None:
        for item in self.ctx.items():
            if item[0] == 'From':
                # self.email_from = self._get_from(item=item[1])
                pass
            elif item[0] == 'Subject':
                pass
                # self.email_subject = self._get_subject(item=item[1])
            

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
    
    def _extract_payloads(self) -> Generator[email.message.Message, None, None]:
        for payload in self.ctx.get_payload():
            yield payload

    