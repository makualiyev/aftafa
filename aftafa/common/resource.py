from abc import ABC, abstractmethod
from hashlib import md5
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import random
import string
import shutil
import json
from typing import Any

import pandas as pd

from aftafa.common.loader import Loader
from aftafa.client.baseclient import BaseClient
from aftafa.utils.helpers import sizeof_fmt


class Resource(ABC):
    def __init__(self) -> None:
        self.is_extractable: bool = True
        self.is_empty: bool = False
        pass

    @abstractmethod
    def extract(self) -> None:
        pass

    @abstractmethod
    def get_loader(self) -> Loader:
        pass
    
    
class HTTPResource(Resource):
    def __init__(self) -> None:
        super().__init__()

    def extract(self, client: BaseClient) -> None:
        return super().extract()
    
    def get_loader(self) -> Loader:
        return super().get_loader()
    

class EmailResource(Resource):
    """Email resource is implemented via Yandex Mail
    client class in ../client/mail/client.py. Ideally
    it should get emails from Mail Server (IMAP Protocol)
    and parse them to get the payloads and pass them to                 # TODO: or save .eml files and parse them later?
    FileLoader."""
    def __init__(self) -> None:
        super().__init__()

    def _extract_as_eml(self) -> None:
        pass

    def extract(self, naive: bool = False) -> None:
        if naive:
            self._extract_as_eml()
            return
        return
    
    def get_loader(self) -> Loader:
        return super().get_loader()


class FileResource(Resource):
    def __init__(self, path: Path) -> None:
        super().__init__()
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"There is no file with the given path!")
        self.file_path: Path = path
        self.file_name: str = path.stem
        self.file_extension: str = path.suffix
        self.file_hash: str = self._get_file_hash()
        self.file_size: int = path.stat().st_size
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

    
    def get_loader(self) -> Loader:
        return super().get_loader()


class JSONResource(FileResource):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
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
    
    def get_loader(self) -> Loader:
        return super().get_loader()
    

class ExcelResource(FileResource):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
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
            with pd.ExcelFile(self.file_path) as xl:
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
                with pd.ExcelFile(self.file_path) as xl:
                    return xl.sheet_names
                
    def get_dataframe(self, sheet_name: str) -> pd.DataFrame:
        with pd.ExcelFile(self.file_path) as xl:
            return xl.parse(sheet_name=sheet_name)
        
    def _extract_dataframes(self) -> list[pd.DataFrame | None]:
        extracted_dataframes = []
        for sheet_name in self.file_contents_meta['contents']:
            extracted_dataframes.append(
                {
                    sheet_name: self.get_dataframe(sheet_name=sheet_name)
                }
            )
        return extracted_dataframes

    def extract(self, naive: bool = False) -> list[pd.DataFrame | None] | None:
        if naive:
            return self._extract_dataframes()
        return None

    
    def get_loader(self) -> Loader:
        return super().get_loader()
    
