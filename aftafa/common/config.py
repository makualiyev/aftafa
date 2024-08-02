from typing import Any
from pathlib import Path


class Config:
    POSTGRES_DNS_PATH: str = ""
    META_CREDENTIALS_PATH: Path = Path("")

    def __init__(self) -> None:
        self.postgres_url = self._get_postgres_credentials()

    def _get_postgres_credentials(self) -> dict[str, str]:
        with open(self.POSTGRES_DNS_PATH, "r") as f:
            db_url: str = f.readline().strip("\n")
        return db_url

    def _get_meta_credentials_file(self, channel: str) -> dict[str, Any]:
        if channel == "OZ":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta.json"
            return meta_credentials_file
        elif channel == "OD":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta_odata.json"
            return meta_credentials_file
        elif channel == "MAIL":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta.json"
            return meta_credentials_file
        elif channel == "DIADOC":
            meta_credentials_file: Path = (
                self.META_CREDENTIALS_PATH / "meta_diadoc.json"
            )
            return meta_credentials_file
        elif channel == "SBERMM":
            meta_credentials_file: Path = (
                self.META_CREDENTIALS_PATH / "meta_sbermm.json"
            )
            return meta_credentials_file
        elif channel == "MPSTATS":
            meta_credentials_file: Path = (
                self.META_CREDENTIALS_PATH / "meta_mpstats.json"
            )
            return meta_credentials_file
        elif channel == "MV":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta_mv.json"
            return meta_credentials_file
        elif channel == "WB":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta_wb.json"
            return meta_credentials_file
        elif channel == "YA":
            meta_credentials_file: Path = self.META_CREDENTIALS_PATH / "meta_ya.json"
            return meta_credentials_file
