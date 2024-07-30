from db import engine as db_engine


class ChannelCard:
    def __init__(
            self,
            channel: str,
            uid: str,
            sku: str
    ) -> None:
        """
        :params:
        """
        self.channel = channel
        self.uid = uid
        self.sku = sku


class Analyzer:
    def __init__(self) -> None:
        pass
