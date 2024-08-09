from pathlib import Path
import imaplib
import base64
import json
from datetime import datetime
import email
from typing import Generator
import quopri

from aftafa.utils.helpers import sizeof_fmt


class RFC822MessageParser:
    """
    Parser for RFC 822 part of message, witch we get from
    `IMAP4_SSL.fetch()`.
    """
    def __init__(
            self,
            rfc822_message: tuple[bytes]
        ) -> None:
        self.rfc822_message: tuple[bytes] = rfc822_message[1]
        self.rfc822_metadata: dict[str, str | int] = self._parse_metadata_part(metadata_raw=rfc822_message[0])

    def _parse_metadata_part(self, metadata_raw: bytes) -> dict[str, str | int]:
        """Parses metadata part.

        Args:
            metadata_raw (bytes): metadata in bytes (answer from `.fetch` command)

        Returns:
            dict[str, str | int]: returned in a more readable way
        """
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


class IMAPClient:
    """
    IMAP client for interacting with mail server
    (e. g. Yandex Mail).

    Args:
        user (str): username that maps username and
        password from config file.
        config (str): config file.

    Raises:
        KeyError: if no entry for the user in con-
        fig.

    Returns:
        None: initialize IMAP4_SSL class
    """
    def __init__(
            self,
            config_file: str | Path
    ) -> None:
        self._config: dict[str, str | int] = self._set_config_from_file(config_file_path=config_file)
            
    def _set_config_from_file(self, config_file_path: str | Path) -> None:
        if isinstance(config_file_path, str):
            config_file_path = Path(config_file_path)
        if not config_file_path.exists():
            raise FileNotFoundError(f"There is no file with the given path!")
        
        with open(config_file_path, 'rb') as f:
            config = json.load(f)
        return config

    @property
    def _state(self) -> str | None:
        "state = AUTH"
        return self.mail.state
    
    def _login(self) -> None:
        if not 'mail' in self.__dict__:
            self.mail = imaplib.IMAP4_SSL(
                host=self._config.get('imap_host_url'), port=self._config.get('imap_host_port')
            )
        try:
            self.mail.login(
                self._config.get('imap_username'),
                self._config.get('imap_password')
            )
        except imaplib.IMAP4.error as imap4_login_err:
            print(f"IMAP4.error: {imap4_login_err}")
            print(f"Can't login with provided credentials for '{self.imap_username}'!")
            return None
        return None
    
    def _close(self) -> None:
        if self._state == "SELECTED":
            self.mail.close()
        self.mail.logout()

    def __enter__(self):
        self.mail = imaplib.IMAP4_SSL(
            host=self._config.get('imap_host_url'),
            port=self._config.get('imap_host_port')
        )
        if self._state == "NONAUTH":
            self._login()
            return self
        else:
            raise ValueError(f"status of IMAP4_SSL is not `NONAUTH`")

    def __exit__(self, *args):
        self._close()

    def _list_mailboxes(self, mailbox: str = '""', pattern: str = '*') -> None:
        """convenience method

        Args:
            mailbox (str, optional): _description_. Defaults to '""'.
            pattern (str, optional): _description_. Defaults to '*'.

        Returns:
            _type_: _description_
        """
        mail_listed: tuple[bytes, list[bytes]] = self.mail.list(directory=mailbox, pattern=pattern)
        status, result = mail_listed
        if status != 'OK':
            return None
        return [''.join(i.decode().split('"|"')[1:])[1:].replace('"', "") for i in result]


    
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
            mailbox: str,
            email_since: str | None = None,
            email_subject: str = "",
            email_from: str = ""
    ) -> list[bytes] | None:
        """Searches in a given mailbox and returns
        list of bytes of message ids.

        Args:
            mailbox (str): _description_
            email_since (str | None, optional): _description_. Defaults to None.
            email_subject (str, optional): _description_. Defaults to "".
            email_from (str, optional): _description_. Defaults to "".

        Returns:
            list[bytes] | None: a list of message UIDs in bytes string,
            e. g. b'1 2 3'
        """
        selected_mailbox: str = self._select_mailbox(mailbox=mailbox)
        if selected_mailbox != 'OK':
            return None
        
        if not email_since:
            email_since = datetime.today()
        else:
            email_since = datetime.strptime(email_since, '%Y-%m-%d')
        date_string: str = f'SINCE "{email_since.strftime("%d-%b-%Y")}"'
        
        if email_from:
            email_from = f' FROM "{email_from}"'
        if email_subject:
            email_subject = f'SUBJECT "{email_subject}" '

        search_query: str = f'({email_subject}{date_string}{email_from})'
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
                    b'28 (RFC822 {103743}',         # uid of message and `message_parts` 
                                                    # argument (standard) for IMAP fetch method
                                                    #
                    b'Received: from...',           # message itself
                ),                                  # 
                b')'                                # closing bracket byte
            ]                                       #
        )                                           #
        
        Unpacking status and data into separate variables to work on it. We
        are interested in message itself, which is `fetched_data[0][1]`, so
        naive implementation would be this. TODO: think of improving this method
        to be more error-prone.

        Args:
            message_id (bytes): the UID of message that's been previously
            searched.

        Returns:
            list[tuple[bytes], bytes] | list[None]: returns raw fetched data by
            message UID in bytes.
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
        """After we've fetched message using `_fetch_email` method we want
        to check if it has the same structure as it is described in the
        standard. The method returns just email part if the check is suc-
        cessfull and logs odd results.

        Args:
            message_data (list[tuple[bytes], bytes]): raw message data that
            we get from `FETCH` command.

        Returns:
            _type_: 
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
            limit: int = 0,
            email_since: str | None = None,
            email_subject: str = "",
            email_from: str = ""
    ) -> Generator[list[dict[str, str | bytes]] | list[None], None, None]:
        """Searches in a given mailbox and returns list of bytes of message
        ids.

        Args:
            mailbox (str): _description_
            limit (int): Get first `limit` mails.
            email_since (str | None, optional): Get mails from the given date
            in this format %Y-%m-%d. Defaults to None.
            email_subject (str, optional): _description_. Defaults to "".
            email_from (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_

        Yields:
            Generator[list[dict[str, str | bytes]] | list[None], None, None]: _description_
        """
        email_list: list = []
        search_result: list[bytes] | None = self._search_mailbox(
                                                mailbox=mailbox,
                                                email_since=email_since,
                                                email_subject=email_subject,
                                                email_from=email_from
                                            )
        if not search_result:
            print(f"No mailbox!")
            return None
        
        if not search_result[0]:
            print(f"No emails for this date!")
            return None
        
        # e. g. search_result is something like [(b'1 2 3', b'(RFC 822)')]
        target_message_uids: list[bytes] = search_result[0].split()
        if not limit:
            limit = len(target_message_uids)
        
        for search_result_message_id in target_message_uids[:limit]:
            fetched_message: list[tuple[bytes], bytes] | list[None] = self._fetch_email(message_id=search_result_message_id)
            extracted_rfc822_parts: list[dict[str, str | int], bytes] = self._extract_rfc822_parts(message_data=fetched_message)
            fetched_message_metadata, fetched_message_data = extracted_rfc822_parts

            if fetched_message:
                yield {
                    'metadata': fetched_message_metadata,
                    'data': fetched_message_data
                }


class SMTPClient:
    """
    SMTP client for interacting with mail server
    (e. g. Yandex Mail).

    Args:
        user (str): username that maps username and
        password from config file.
        config (str): config file.

    Raises:
        KeyError: if no entry for the user in con-
        fig.

    Returns:
        None: initialize ? class
    """
    def __init__(
            self,
            host_url: str = "smtp.yandex.com",
            host_port: int = 993,
            user_config: str = '',
            user: str = 'magsud_delventa'
    ) -> None:
        self.SMTP_HOST_URL: str = host_url
        self.SMTP_HOST_PORT: int = host_port
        self.username: str = ""
        self.password: str = ""

        try:
            self.username = ''              # TODO: add credentials info
            self.password = ''              # TODO: add credentials info
        except KeyError as key_err:
            if key_err.args[0] == f"{user}":
                print(f"There are no credentials provided for user '{user}'")
            else:
                print(key_err)

    def send_email(self) -> None:
        """TBI
        """
        pass
        


def escape_b64(encoded_: str) -> str:
    try:
        r = base64.b64decode(encoded_.lstrip('=?UTF-8?B?').rstrip('?=') + '=').decode('utf-8')
    except UnicodeDecodeError:
        r = base64.b64decode(encoded_.lstrip('=?utf-8?B?').rstrip('?=') + '==').decode('utf-8')
    return r

def escape_b64_from_koi8_r(msg_: str) -> str:
    return email.base64mime.decodestring(msg_.split('?')[3]).decode('koi8-r')
    # return base64.b64decode(msg_.split('?')[3].encode('utf-8')).decode('koi8-r')
