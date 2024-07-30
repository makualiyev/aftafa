import imaplib
import base64
import json
from datetime import datetime
from dataclasses import dataclass
import email
import quopri

from aftafa.common.config import Config
from aftafa.utils.helpers import color_fmt, sizeof_fmt



# META_DIR = r'E:/shoptalk/local_/meta/meta.json'
with open(Config()._get_meta_credentials_file(channel='MAIL'), 'rb') as f:
    META = json.loads(f.read())


class RFC822MessageParser:
    def __init__(
            self,
            rfc822_message: tuple[bytes]
        ) -> None:
        self.rfc822_message: tuple[bytes] = rfc822_message[1]
        self.rfc822_metadata: dict[str, str | int] = self._parse_metadata_part(metadata_raw=rfc822_message[0])

    def _parse_metadata_part(self, metadata_raw: bytes) -> dict[str, str | int]:
        message_part = metadata_raw.split()
        uid = int(message_part[0].decode())
        standard = message_part[1].decode().replace('(', '').replace(' ', '')
        size_in_bytes = int(message_part[2].decode()[1:-1])
        return {
            'uid': uid,
            'standard': standard,
            'size_in_bytes': size_in_bytes,
            'size': sizeof_fmt(num=size_in_bytes)
        }
    
    def _check_other_parts(self) -> None:
        """Checking for other parts of RFC822 message."""
        pass


class YandexMailClient:
    IMAP_HOST_URL: str = "imap.yandex.com"
    IMAP_HOST_PORT: int = 993

    def __init__(
            self,
            user: str = 'magsud_delventa'
    ) -> None:
        self.username: str = ""
        self.password: str = ""
        try:
            self.username = META['mails'][user]['username']
            self.password = META['mails'][user]['password']
        except KeyError as key_err:
            if key_err.args[0] == f"{user}":
                print(f"There are no credentials provided for user '{user}'")
            else:
                print(key_err)
            

    @property
    def _state(self) -> str | None:
        "state = AUTH"
        return self.mail.state
    
    def _login(self) -> None:
        if not 'mail' in self.__dict__:
            self.mail = imaplib.IMAP4_SSL(host=self.IMAP_HOST_URL, port=self.IMAP_HOST_PORT)
        try:
            self.mail.login(self.username, self.password)
        except imaplib.IMAP4.error as imap4_login_err:
            print(f"IMAP4.error: {imap4_login_err}")
            print(f"Can't login with provided credentials for '{self.username}'!")
            return None
        return None
    
    def _close(self) -> None:
        if self._state == "SELECTED":
            self.mail.close()
        self.mail.logout()

    def __enter__(self):
        self.mail = imaplib.IMAP4_SSL(host=self.IMAP_HOST_URL, port=self.IMAP_HOST_PORT)
        if self._state == "NONAUTH":
            self._login()
            return self
        else:
            raise ValueError(f"status of IMAP4_SSL is not `NONAUTH`")

    def __exit__(self, *args):
        self._close()
    
    def _select_mailbox(self, mailbox: str) -> str:
        try:
            selected_mailbox_status, selected_mailbox_data = self.mail.select(mailbox=mailbox)
        except imaplib.IMAP4.abort as imap4_abort_err:
            assert 'socket error: EOF occurred in violation of protocol' in imap4_abort_err.args[0], 'some other error with IMAP4.abort -> '
            print(f"IMAP4.abort: {imap4_abort_err}")
            print(f"Connection to socket lost, try to login again!")
            return None
        
        if selected_mailbox_status != 'OK':
            print(f"Can't select mailbox `{mailbox}` with status `{selected_mailbox_status}`, still in state 'AUTH'")
            return selected_mailbox_status
        return selected_mailbox_status

    def _search_mailbox(
            self,
            folder: str,
            date_: str | None = None,
            subject: str = "",
            from_: str = ""
    ) -> list[bytes] | None:
        """Searches in a given mailbox
        and returns list of bytes of message ids
        """
        selected_mailbox: str = self._select_mailbox(mailbox=folder)
        if selected_mailbox != 'OK':
            return None
        
        if not date_:
            date_ = datetime.today()
        else:
            date_ = datetime.strptime(date_, '%Y-%m-%d')
        date_string = date_.strftime('%d-%b-%Y')
        
        if from_:
            from_ = f' FROM "{from_}"'
        if subject:
            subject = f'SUBJECT "{subject}" '


        search_query: str = f'({subject}SINCE "{date_string}"{from_})'
        print(f'THE SEARCH QUERY IS ---> {search_query}')
        try:
            status, data = self.mail.search(None, search_query)
        except imaplib.IMAP4.error as imap4_err:
            print(f"IMAP4.error: {imap4_err}")
            return None
        except imaplib.IMAP4.abort as imap4_abort_err:
            assert 'socket error: EOF' in imap4_abort_err.args[0], 'some other error with IMAP4.abort -> '
            print(f"IMAP4.abort: {imap4_abort_err}")
            return None
        try:
            assert status == 'OK', f"not OK status for this search query {search_query}, but this status -> {status}."
        except AssertionError as e:
            print(e)
            
        return data
    

    def _fetch_email(self, message_id: bytes) -> list[tuple[bytes], bytes] | list[None]:
        """Fetches email via IMAP protocol. The `fetch` method of imaplib
        returns a tuple with a status of `FETCH` (`uid`) command and a list
        of data that consists of a tuple of bytes + a byte with the closing
        bracket, e. g. :
        (                                           #
            'OK',                                   # status of a `fetch` command
            [                                       #
                (                                   # a tuple of message parts
                    b'28 (RFC822 {103743}',         # uid of message and `message_parts` argument (standard) for IMAP fetch method
                    b'Received: from...',           # message itself
                ),                                  # 
                b')'                                # closing bracket byte
            ]                                       #
        )                                           #
        
        Unpacking status and data into separate variables to work on it. We
        are interested in message itself, which is `fetched_data[0][1]`, so
        naive implementation would be this. TODO: think of improving this method
        to be more error-prone.
        """
        if self._state != 'SELECTED':
            return []
        status, data = self.mail.fetch(message_id, '(RFC822)')
        try:
            assert status == 'OK', f"not OK status for this fetched mail {message_id.decode()}, but this status -> {status}."
        except AssertionError as e:
            print(e)
            return []
        return data
    
    def _extract_rfc822_parts(self, message_data: list[tuple[bytes], bytes]) -> None:
        """
        After we've fetched message using `_fetch_email` method we want
        to check if it has the same structure as it is described in the
        standard. The method returns just email part if the check is suc-
        cessfull and logs odd results.
        """
        if not isinstance(message_data, list):
            print(f"func:_extract_rfc822: type of fetched message parts are not compliant, type -> {type(message_data)}")
            return None
        
        if len(message_data) == 1:
            print(f"func:_extract_rfc822: there are no `b')'` ending byte here -> {message_data[0]}")
            return None
        
        for idx, message_data_part in enumerate(message_data):
            if idx == 0:
                ass_tuple: bool = isinstance(message_data_part, tuple)
                ass_tuple_child_bytes: bool = all([isinstance(i, bytes) for i in message_data_part])
                assert ass_tuple and ass_tuple_child_bytes, f"func:_extract_rfc822: first part is not a tuple!"
                # checking tuple itself
                rfc822_message_parser: RFC822MessageParser = RFC822MessageParser(message_data_part)
                continue
            if not isinstance(message_data_part, bytes):
                print(f"func:_extract_rfc822: some message data parts are not in bytes! -> part:{message_data_part} - type:{type(message_data_part)}")
                continue
        
        return [
            rfc822_message_parser.rfc822_metadata,
            rfc822_message_parser.rfc822_message
        ]
        

    def _parse_email(self, data: bytes) -> None:                        # TODO: to be implemented
        pass


    def get_email(
            self,
            mailbox: str,
            email_since: str | None = None,
            email_subject: str = "",
            email_from: str = ""
    ) -> None:
        """Searches in a given mailbox
        and returns list of bytes of message ids
        """
        email_list: list = []
        search_result: list[bytes] | None = self._search_mailbox(
                                                folder=mailbox,
                                                date_=email_since,
                                                subject=email_subject,
                                                from_=email_from
                                            )
        if not search_result:
            print(f"No mailbox!")
            return None
        
        if not search_result[0]:
            print(f"No emails for this date!")
            return None
        
        # e. g. search_result is something like [(b'1 2 3', b'(RFC 822)')]
        for search_result_message_id in search_result[0].split():
            fetched_message: list[tuple[bytes], bytes] | list[None] = self._fetch_email(message_id=search_result_message_id)
            extracted_rfc822_parts: list[dict[str, str | int], bytes] = self._extract_rfc822_parts(message_data=fetched_message)
            fetched_message_metadata, fetched_message_data = extracted_rfc822_parts

            if fetched_message:
                email_list.append({
                    'metadata': fetched_message_metadata,
                    'data': fetched_message_data
                })
        return email_list


        


def escape_b64(encoded_: str) -> str:
    try:
        r = base64.b64decode(encoded_.lstrip('=?UTF-8?B?').rstrip('?=') + '=').decode('utf-8')
    except UnicodeDecodeError:
        r = base64.b64decode(encoded_.lstrip('=?utf-8?B?').rstrip('?=') + '==').decode('utf-8')
    return r

def escape_b64_from_koi8_r(msg_: str) -> str:
    return email.base64mime.decodestring(msg_.split('?')[3]).decode('koi8-r')
    # return base64.b64decode(msg_.split('?')[3].encode('utf-8')).decode('koi8-r')


# def process_payloads(email_) -> None:
#     email_payloads = email_.get_payload()
#     email_date = datetime.strptime(email_.get('Date'), '%a, %d %b %Y %H:%M:%S +0300')
#     assert len(email_payloads) == 2, "Something's changed in email attachments mechanism"
#     for email_payload in email_payloads:
#         if email_payload.get_content_type() == 'text/plain':
#             continue
#         email_attachment = email_payload
    
#     assert escape_b64(email_attachment.get_filename()) == 'Остаток на складах МВМ_Дельвента.xlsx', "File name for the attachment is changed"
#     os.chdir(r'E:\shoptalk\marketplace_\MV\OOO_DELVENTA\stocks')
#     with open(f'mvm_stocks_{email_date.strftime("%d-%m-%Y")}.xlsx', 'wb') as f:
#         f.write(base64.b64decode(email_attachment.get_payload()))
#     print(f'Successfully saved for this date -> {email_date.strftime("%Y-%m-%d")}')
    
# def process_mail(mail_: imaplib.IMAP4_SSL, uid_: bytes) -> None:
#     mail_element_status, mail_element_data = mail_.fetch(uid_, '(RFC822)')
#     mail_element_message = email.message_from_bytes(mail_element_data[0][1])
#     mail_element_subject = escape_b64(mail_element_message.get('Subject'))
    

#     assert len(mail_element_data) == 2, f"Somethings's changed in mail_element_data, it now consists of more than 2 elements"
#     assert mail_element_subject == 'Остаток на складах МВМ', f"Not the same name for the subject"

#     process_payloads(email_=mail_element_message)
