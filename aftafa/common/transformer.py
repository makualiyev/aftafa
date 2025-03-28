
class Transformer:
    def __init__(self, kind: str) -> None:
        self.kind = kind


class PandasTransformer(Transformer):
    def __init__(
        self,
        spec: dict[str, str],
        kind: str = "pandas"
    ) -> None:
        super().__init__(kind)
        self.spec = spec

    # def _feed_dataframe(df: pd.DataFrame)

