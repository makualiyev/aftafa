from typing import Any
from pathlib import Path


class Config:
    POSTGRES_DNS_PATH: str = ""
    META_CREDENTIALS_PATH: Path = Path("")

    def __init__(self) -> None:
        # self.postgres_url = self._get_postgres_credentials()
        pass

    # def _get_postgres_credentials(self) -> dict[str, str]:
    #     with open(self.POSTGRES_DNS_PATH, "r") as f:
    #         db_url: str = f.readline().strip("\n")
    #     return db_url

    def _get_meta_credentials_file(self, channel: str) -> dict[str, Any]:
        pass
