import json
from pathlib import Path
import smtplib


class SMTPClient:
    """
    SMTP client for interacting with mail server
    (e. g. Yandex Mail).

    Args:
        user (str): username that maps username and
        password from config file.
        config (str): config file.

    Returns:
        None: initialize SMTP_SSL class
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
    
    def _login(self) -> None:
        if not 'mail' in self.__dict__:
            self.mail = smtplib.SMTP_SSL(
                host=self._config.get('smtp_host_url'),
                port=self._config.get('smtp_host_port')
            )

        login_result: tuple[int, bytes] = self.mail.login(
                            self._config.get('smtp_username'),
                            self._config.get('smtp_password')
                        )
        login_result_status, login_result_data = login_result
        if login_result_status == 235:
            return None
        elif login_result_status == 503:
            return None
        else:
            print(f"Unknown status while login -> {login_result_status}")
            print(f"Unknown status: {login_result_data}")
        return None
    
    def _close(self) -> None:
        try:
            self.mail.quit()
        except smtplib.SMTPServerDisconnected as e:
            self.mail.close()

    def __enter__(self):
        self.mail = smtplib.SMTP_SSL(
            host=self._config.get('smtp_host_url'),
            port=self._config.get('smtp_host_port')
        )
        self._login()
        return self

    def __exit__(self, *args):
        self._close()

    def send_email(self) -> None:
        pass
    