from datetime import datetime
from pathlib import Path, WindowsPath
import os
import json


def resolve_os() -> str:
    if os.name == 'nt':
        return 'windows'
    return 'linux'


def resolve_paths() -> dict[str, str]:
    with open("ec_client/diadoc/config.json", "rb") as f:
        configs = json.load(f)

    for k, v in configs.items():
        configs[k] = Path(v)

    return configs


class ConfigResolver:
    def __init__(self) -> None:
        with open("ec_client/diadoc/config.json", "rb") as f:
            self.configs_raw = json.load(f)
        self.last_ts = self._get_last_updated_ts()

    def resolve_paths(self) -> dict[str, WindowsPath]:
        resolved_paths = {}
        for k, v in self.configs_raw.items():
            if k in ('zip_path', 'doc_path'):
                resolved_paths[k] = Path(v)
        return resolved_paths
    
    def _get_last_updated_ts(self) -> str:
        ts = self.configs_raw.get('state')
        return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
    
    def update_state(self) -> None:
        updated_configs = self.configs_raw
        updated_configs['state'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        with open("ec_client/diadoc/config.json", "w") as f:
            json.dump(updated_configs, f)
        return None