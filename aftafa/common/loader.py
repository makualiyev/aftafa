import json
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any

from aftafa.utils.helpers import parse_jsonpath


class Loader(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def load(self) -> None:
        pass


class FileLoader(Loader):
    """Abstract FileLoader class."""
    def __init__(self, output_path: str | None) -> None:
        if not Path(output_path).is_dir():
            raise FileNotFoundError("")
        self._path = Path(output_path)
    
    def generate_random_ts(self) -> str:
        return datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    def load(self, data: bytes) -> None:
        if data:
            with open((self._path / f'xml_loaded_{self.generate_random_ts()}.dat'), 'wb') as f:
                f.write(data)


class XMLLoader(FileLoader):
    def __init__(self, output_path: str | None) -> None:
        super().__init__(output_path)

    def load(self, data: str) -> None:
        with open((self._path / f'xml_loaded_{self.generate_random_ts()}.xml'), 'w', encoding='utf-8') as f:
            f.write(data)


class JSONLoader(FileLoader):
    def __init__(self, output_path: str | None) -> None:
        super().__init__(output_path)

    def _validate_data(self, data: dict[str, Any] | bytes) -> None:
        if isinstance(data, bytes):
            return json.loads(data.decode())
        return data

    def load(self, data: dict[str, Any]) -> None:
        data = self._validate_data(data=data)
        with open((self._path / f'json_loaded_{self.generate_random_ts()}.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            

class JSONlLoader(FileLoader):
    def __init__(
            self,
            output_path: str | None,
            jsonpath: str = ''
    ) -> None:
        super().__init__(output_path)
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


class SQLLoader(Loader): 
    def __init__(self) -> None:
        super().__init__()

    def load(self) -> None:
        pass



if __name__ == '__main__':
    jl = JSONLoader()
    print('ok')
    