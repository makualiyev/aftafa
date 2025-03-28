from abc import ABC, abstractmethod
from datetime import datetime
from hashlib import md5
from pathlib import Path, PosixPath
from zipfile import ZipFile, ZIP_DEFLATED
import random
import string
import shutil
import json
from typing import Any, Generator, Union

from pandas import ExcelFile, DataFrame

from aftafa.client.mail.imap_client import IMAPClient
from aftafa.client.mail.parser import EmailParser
from aftafa.client.baseclient import BaseClient
from aftafa.utils.helpers import sizeof_fmt


class DataSourceConfiguration(ABC):
    def __init__(self) -> None:
        pass


class DataSource(ABC):
    """Abstract class for data sources.

    Args:
        ABC (_type_): _description_
    """
    def __init__(self) -> None:
        self._source_type: str = "abstract"
        self.is_extractable: bool = True
        self.is_empty: bool = False
        self.configuration: DataSourceConfiguration | None = None

    @abstractmethod
    def extract(self) -> None:
        pass


class HTTPDataSource(DataSource):
    def __init__(
        self
    ) -> None:
        super().__init__()
        self._source_type = "http"

    def extract(self) -> None:
        pass


class RESTAPIDataSource(DataSource):
    """REST API Data source basic implementation
    which can fetch data using `client` or `connection`.

    Args:

    
    Methods:
        extract (client): _description_
    """
    def __init__(
        self,
        method: str,
        path: str,
        client: BaseClient | None
    ) -> None:
        super().__init__()
        self._source_type: str = "restapi"
        self.method: str = method.upper()
        self.path: str = self._sanitize_path(path)
        self.client: BaseClient | None = client
        self.kwargs: dict[str, Any] = {}

    def _set_kwargs(self, **kwargs) -> None:
        self.kwargs = kwargs
        return None
    
    def _sanitize_path(self, path: str) -> None:
        if not path.startswith("/"):
            path = ''.join(["/", path])
        return path

    def _check_connection(self) -> None:
        pass

    def extract(self, client: BaseClient | None = None, naive: bool = False, **kwargs) -> Generator[list[dict[Any | Any]], None, None] | None:
        if not client:
            client = self.client
        if not self.client and not client:
            raise ValueError("Didn't provide a BaseClient for connection!")
        
        if not kwargs:
            kwargs = self.kwargs
        
        extraction_ts: str = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        with client.request(
                    method=self.method,
                    url=self.path,
                    **kwargs
                ) as req:
            if req.status_code == 200:
                data = {
                    "__source_type": "json",
                    "metadata": {
                        "client": self.client._client_name,
                        "name": '__'.join([
                                    self.client._client_name,
                                    self.method.lower(),
                                    '__'.join(self.path[1:].split('/'))
                                ]),
                        "extraction_ts": extraction_ts
                    },
                    "data": req.json()
                }
                yield data
    

class EmailDataSource(DataSource):
    """Email resource is implemented via Yandex Mail
    client class in ../client/mail/client.py. Ideally
    it should get emails from Mail Server (IMAP Protocol)
    and parse them to get the payloads and pass them to                         # TODO: or save .eml files and parse them later?
    FileLoader.

    Args:
        DataSource (_type_): _description_

    Methods:
        _extract_as_eml (None): _description_
        extract (None): _description_
    """
    def __init__(self, configs: dict[str, str]) -> None:
        super().__init__()
        self._source_type = "email"
        self._configs = configs
        self._credentials: dict[str, Any] = self._set_credentials_from_file(credentials_file_path=self._configs.get('credentials_file'))

    def _set_credentials_from_file(self, credentials_file_path: str | Path) -> dict[str, str] | None:
        if isinstance(credentials_file_path, str):
            credentials_file_path = Path(credentials_file_path)
        if isinstance(credentials_file_path, PosixPath):
            credentials_file_path = credentials_file_path.expanduser()
        if not credentials_file_path.exists():
            raise FileNotFoundError(f"There is no file with the given path! [{credentials_file_path}]")
        with open(credentials_file_path, 'rb') as f:
            credentials = json.load(f)
        return credentials
    
    def _init_mail(self) -> Generator[list[dict[str, str | bytes]] | list[None], None, None]:
        with IMAPClient(configs=self._configs, credentials=self._credentials) as client:
            for fetched_email_data in client.get_email(
                                mailbox=self._configs.get('mailbox'),
                                limit=self._configs.get('email_limit'),
                                email_since=self._configs.get('email_since'),
                                email_from=self._configs.get('email_from')
                            ):
                yield fetched_email_data

    def _extract_as_eml(self) -> Generator[list[dict[str, str | bytes]] | list[None], None, None]:
        yield from self._init_mail()

    def _extract_attachments(self, attachment_file_type_accept: str | None = None) -> Generator[ dict[str, Any] | None, None, None]:
        if not attachment_file_type_accept:
            self._configs.get('attachment_file_type_accept')
        for fetched_email_data in self._init_mail():
            parsed_email: EmailParser = EmailParser(ctx=fetched_email_data)
            for attachment in parsed_email.attachments:
                if attachment.decoded_file_extension in attachment_file_type_accept.split(';'):
                    attachment = attachment.__dict__
                    attachment['__source_type'] = self._source_type
                    yield attachment

    def extract(self, naive: bool = False) -> Generator[list[dict[str, str | bytes]] | list[None], None, None] | None:
        if naive:
            return self._extract_as_eml()
        if self._configs.get('attachment_only'):
            return self._extract_attachments(attachment_file_type_accept=self._configs.get('attachment_file_type_accept'))
        return None



class FileDataSource(DataSource):
    def __init__(
            self,
            path: Path,
            is_single: bool = True,
            query: Union[dict[str, Union[str, int, bool]], None] = None
        ) -> None:
        """File Data source base class
        - File
            - JSON
            - Excel
            - XML
            - CSV
            - etc.

        Args:
            path (Path): path of file source
            is_single (bool, optional): if it is folder or not. Defaults to True.
            query (Union[dict[str, Union[str, int, bool]], None], optional): query to file. Example:
            {
                `since_from`: `today`,
                `since_from_delta`: `1 day`,
                `search_string`: `Отчет об остатках товара`,
                `limit`: 1
            }
            Defaults to None.

        Raises:
            FileNotFoundError: _description_
        """
        super().__init__()
        self._source_type = "file"

        if isinstance(path, str):
            path = Path(path)
        if isinstance(path, PosixPath):
            path = path.expanduser()
        if not path.exists():
            raise FileNotFoundError(f"There is no file with the given path!")

        if is_single:
            self.file_path: Path = path
        else:
            self.file_path: Path = self._resolve_folder_query(query=query, path=path)
        
        self.file_name: str = self.file_path.stem
        self.file_extension: str = self.file_path.suffix
        self.file_hash: str = self._get_file_hash()
        self.file_size: int = self.file_path.stat().st_size
        self.is_extractable: bool = True
        self.is_empty: bool = False
        
        if self.file_size == 0:
            print(f"File {self.file_name} is empty!")
            self.is_empty = True
            self.is_extractable = False
        
        self.file_contents_meta = {
            "name": self.file_name,
            "path": str(self.file_path),
            "extension": self.file_extension,
            "hash": self.file_hash,
            "size": self.file_size,
            "human_size": sizeof_fmt(self.file_size)
        }
        
    def _resolve_folder_query(
        self,
        query: Union[dict[str, Union[str, int, bool]], None],
        path: Path
    ) -> Path:
        if not path.is_dir():
            raise FileNotFoundError(
                f"You've provided multiple files argument, but path of a file is provided"
            )
        if not query:
            queried_path: Path = sorted(list(path.glob('*.*')), key=lambda x: x.stat().st_ctime, reverse=True)[0]           # FIXME: maybe not `st_ctime`
            return queried_path
        
        queried_path: Path = [
            path
            for path in sorted(list(path.glob(f"{query.get('search_string')}*.*")), key=lambda x: x.stat().st_ctime, reverse=True)
            if datetime.fromtimestamp(path.stat().st_ctime) > (datetime.strptime(datetime.today().strftime('%d-%m-%Y'), '%d-%m-%Y'))
        ][:(query.get('limit'))]
        return queried_path[0]                                                                                              # FIXME: think about generators for folder repr

                

    def _get_file_hash(self) -> str:
        with open(self.file_path, 'rb') as f:
            file_hash = md5(f.read()).hexdigest()
        return file_hash

    def extract(self, naive: bool = False) -> bytes | None:
        if naive:
            with open(self.file_path, 'rb') as f:
                file_bytes_content = f.read()
                return file_bytes_content

        return None




class JSONDataSource(FileDataSource):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._source_type = "json"
        if self.file_extension not in ('.json', '.JSON', '.jsonl', '.JSONL'):
            raise TypeError("Not valid JSON file!")
        # self.file_contents_meta['contents'] = keys?

    def _deserialize(self) -> None:
        if self.is_empty:
            return None
        
        with open(self.file_path, 'rb') as f:
            try:
                self._deserialized: str | None = json.dumps(json.load(f), ensure_ascii=False)
            except json.decoder.JSONDecodeError as json_decode_err:
                print(f"json.decoder.JSONDecodeError|{json_decode_err}")
                self.is_extractable: bool = False
                self._deserialized: str | None = None
            except UnicodeDecodeError as unicode_err:
                print(f"UnicodeDecodeError|{unicode_err}")
                self.is_extractable: bool = False
                self._deserialized: str | None = None


    def _extract_schema(self) -> None:
        pass

    def _get_contents(self) -> None:
        pass

    def _prepare(self) -> None:
        pass

    def extract(self, naive: bool = False) -> str | None:
        if naive:
            self._deserialize()
            return self._deserialized
        return None


class CSVDataSource(FileDataSource):
    def __init__(
        self,
        path: Path,
        is_single: bool = False,
        query: str | None = None
    ) -> None:
        super().__init__(path, is_single, query)
        self._source_type = "csv"
        if self.file_extension not in ('.csv', '.CSV'):
            raise TypeError("Not valid CSV file!")
        self.file_contents_meta['contents'] = self._extract_metadata_contents()

    def _extract_metadata_contents(self) -> list[str | None]:
        # try:
        #     with ExcelFile(self.file_path) as xl:
        #         return xl.sheet_names
        # except ValueError as val_err:
        #     if val_err.args[0] == "Excel file format cannot be determined, you must specify an engine manually.":
        #         print(val_err)
        #         print(f"{self.file_name} is not a valid (temporary lock `~$_.xlsx`) or empty Excel file!")
        #         self.is_extractable = False
        #         return []
        # except KeyError as key_err:
        #     if key_err.args[0] == "There is no item named 'xl/sharedStrings.xml' in the archive":
        #         print(key_err)
        #         self._sanitize_xl_file()
        #         with ExcelFile(self.file_path) as xl:
        #             return xl.sheet_names
        pass
                
    def _set_transformer(self, transformer: dict[str, str]) -> None:
        if transformer.get('name') == 'pandas':
            self.transformers.append(transformer.get('commands'))
            return None
        
    def _extract_as_dataframe(self) -> Generator[dict[str, DataFrame], None, None]:
        for sheet_name in self.file_contents_meta['contents']:
            extracted_dataframe = {}
            extracted_dataframe['metadata'] = self.file_contents_meta
            extracted_dataframe['sheet_name'] = sheet_name
            extracted_dataframe['dataframe'] = self._get_dataframe_by_sheetname(sheet_name=sheet_name)
            extracted_dataframe['__source_type'] = 'excel'
            yield extracted_dataframe

    def extract(self, naive: bool = False) -> Generator[DataFrame | None, None, None] | None:
        if naive:
            yield from self._extract_as_dataframe()
        return None
    

class ExcelDataSource(FileDataSource):
    def __init__(
        self,
        path: Path,
        is_single: bool = False,
        query: str | None = None
    ) -> None:
        super().__init__(path, is_single, query)
        self._source_type = "excel"
        if self.file_extension not in ('.xlsx', '.xls', '.XLSX', '.XLS'):
            raise TypeError("Not valid Excel file!")
        self.file_contents_meta['contents'] = self._extract_xl_sheet_names()

    def _sanitize_xl_file(self) -> None:
        with (
            ZipFile(self.file_path, mode='a') as zip_file,
            ZipFile(self.file_path.parent / ''.join([self.file_name, '_new', self.file_extension]), mode='x') as new_zip_file
        ):
            temp_hash: str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            extract_path: Path = Path(self.file_path.parent / f"temp_{temp_hash}")
            zip_file.extractall(path=extract_path)
            Path(extract_path / "xl/SharedStrings.xml").rename(extract_path / "xl/sharedStrings.xml")
            for file_path_ in extract_path.rglob('*'):
                if file_path_.is_file():
                    new_zip_file.write(file_path_, file_path_.relative_to(extract_path), compress_type=ZIP_DEFLATED)

            shutil.rmtree(extract_path)

        Path(self.file_path).unlink()
        Path(self.file_path.parent / ''.join([self.file_name, '_new', self.file_extension])).rename(
            self.file_path.parent / ''.join([self.file_name, self.file_extension])
        )
        pass
        
    def _extract_xl_sheet_names(self) -> list[str | None]:
        try:
            with ExcelFile(self.file_path) as xl:
                return xl.sheet_names
        except ValueError as val_err:
            if val_err.args[0] == "Excel file format cannot be determined, you must specify an engine manually.":
                print(val_err)
                print(f"{self.file_name} is not a valid (temporary lock `~$_.xlsx`) or empty Excel file!")
                self.is_extractable = False
                return []
        except KeyError as key_err:
            if key_err.args[0] == "There is no item named 'xl/sharedStrings.xml' in the archive":
                print(key_err)
                self._sanitize_xl_file()
                with ExcelFile(self.file_path) as xl:
                    return xl.sheet_names
                
    def _set_transformer(self, transformer: dict[str, str]) -> None:
        if transformer.get('name') == 'pandas':
            self.transformers.append(transformer.get('commands'))
            return None

    def _get_dataframe_by_sheetname(self, sheet_name: str) -> DataFrame:
        with ExcelFile(self.file_path) as xl:
            return xl.parse(sheet_name=sheet_name, header=None, index_col=None)
        
    def _extract_dataframes(self) -> Generator[dict[str, DataFrame], None, None]:
        for sheet_name in self.file_contents_meta['contents']:
            extracted_dataframe = {}
            extracted_dataframe['metadata'] = self.file_contents_meta
            extracted_dataframe['sheet_name'] = sheet_name
            extracted_dataframe['dataframe'] = self._get_dataframe_by_sheetname(sheet_name=sheet_name)
            extracted_dataframe['__source_type'] = 'excel'
            yield extracted_dataframe

    def extract(self, naive: bool = False) -> Generator[DataFrame | None, None, None] | None:
        if naive:
            yield from self._extract_dataframes()
        return None
