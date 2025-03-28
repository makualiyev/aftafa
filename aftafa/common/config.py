from typing import Any
from pathlib import Path

import yaml


class Config:
    CONFIG_PATH: Path = Path("aftafa/env/config.yaml")

    def __init__(self) -> None:
        self.configs = self._set_config_from_file(config_file_path=self.CONFIG_PATH)
        self.postgres_url = self.configs.get("database_url")
        self.secrets_path = Path(self.configs.get("secrets_path"))
        self.meta_credentials_path = self.secrets_path / "meta"

    def _set_config_from_file(self, config_file_path: str | Path) -> dict[str, Any]:
        with open(config_file_path, 'r') as f:
            return yaml.load(f, Loader=yaml.Loader)
    
    def _get_meta_credentials_file(self, channel: str) -> dict[str, Any]:
        if channel == 'OZ':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_ozon.json'
            return meta_credentials_file
        elif channel == 'OD':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_odata.json'
            return meta_credentials_file
        elif channel == 'MAIL':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_email.json'
            return meta_credentials_file
        elif channel == 'YA':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_ya.json'
            return meta_credentials_file
        elif channel == 'WB':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_wb.json'
            return meta_credentials_file
        elif channel == 'SM':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_sbermm.json'
            return meta_credentials_file
        elif channel == 'MV':
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_mv.json'
            return meta_credentials_file
        elif channel == "GM":
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_gm.json'
            return meta_credentials_file
        elif channel == "DI":
            meta_credentials_file: Path = self.meta_credentials_path / 'meta_diadoc.json'
            return meta_credentials_file
