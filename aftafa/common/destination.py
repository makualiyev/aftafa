import json
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any

from aftafa.utils.helpers import parse_jsonpath, generate_random_hash


class DataDestination(ABC):
    """Abstract FileDataDestination class.

    Args:
        ABC (_type_): _description_
    """
    def __init__(self) -> None:
        self._destination_type: str = "abstract"

    @abstractmethod
    def load(self) -> None:
        pass


class FileDataDestination(DataDestination):
    """Abstract FileDataDestination class.

    Args:
        DataDestination (_type_): _description_
    """
    def __init__(self, output_path: str | None, file_extension: str = "dat") -> None:
        self._destination_type: str = "file"
        if not Path(output_path).is_dir():
            raise FileNotFoundError("")
        self._path = Path(output_path)
        self.file_extension = file_extension
    
    def generate_random_ts(self) -> str:
        random_hash: str = generate_random_hash()
        timestamp: str = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        return '_'.join([timestamp, random_hash])

    def load(self, data: bytes) -> None:
        filename: str = f'raw_data_loaded_{self.generate_random_ts()}.{self.file_extension}'

        if data and isinstance(data, bytes):
            with open((self._path / filename), 'wb') as f:
                f.write(data)


class XMLDataDestination(FileDataDestination):
    """XML destination

    Args:
        FileDataDestination (_type_): _description_
    """
    def __init__(self, output_path: str | None) -> None:
        super().__init__(output_path)
        self._destination_type: str = "xml"

    def load(self, data: str) -> None:
        with open((self._path / f'xml_loaded_{self.generate_random_ts()}.xml'), 'w', encoding='utf-8') as f:
            f.write(data)


class JSONDataDestination(FileDataDestination):
    """JSON destination

    Args:
        FileDataDestination (_type_): _description_
    """
    def __init__(self, output_path: str | None) -> None:
        super().__init__(output_path)
        self._destination_type: str = "json"

    def _validate_data(self, data: dict[str, Any] | bytes) -> None:
        if isinstance(data, bytes):
            return json.loads(data.decode())
        return data

    def load(self, data: dict[str, Any]) -> None:
        data = self._validate_data(data=data)
        with open((self._path / f'json_loaded_{self.generate_random_ts()}.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            

class JSONlDataDestination(FileDataDestination):
    """JSONl destination

    Args:
        FileDataDestination (_type_): _description_
    """
    def __init__(
            self,
            output_path: str | None,
            jsonpath: str = ''
    ) -> None:
        super().__init__(output_path)
        self._destination_type: str = "jsonl"
        self.jsonpath = jsonpath
        

    def _validate_data(self, data: dict[str, Any] | bytes) -> None:
        if isinstance(data, bytes):
            data = json.loads(data.decode())
        elif isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, list):
            data = data
        elif isinstance(data, dict):
            data = json.loads([data])                                       # FIXME: is it reasonable?
        else:
            raise ValueError(f"DATA provided is in unknown format of JSON -> {data}")
        return data

    def load(self, data: dict[str, Any], jsonpath: str = "") -> None:
        if not data:
            print(f"Failed loading to JSONl file, provided no data!")
            return None
        data = self._validate_data(data=data)
        if self.jsonpath:
            parsed_jsonpath_val: dict | None = parse_jsonpath(jsonpath=self.jsonpath, data=data)
            if parsed_jsonpath_val:
                data = parsed_jsonpath_val

        with open((self._path / f'jsonl_loaded_{self.generate_random_ts()}.jsonl'), 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                for i, entry in enumerate(data):
                    json.dump(entry, f, ensure_ascii=False)
                    if (i + 1) < len(data):
                        f.write('\n')
            else:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')


        return None    


class SQLDataDestination(DataDestination):
    """SQL Data destination

    Args:
        DataDestination (_type_): _description_
    """
    def __init__(self) -> None:
        super().__init__()
        self._destination_type: str = "sql"

    def load(self) -> None:
        pass

