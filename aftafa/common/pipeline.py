from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from aftafa.common.source import DataSource, EmailDataSource
from aftafa.common.destination import DataDestination, FileDataDestination


class PipelineConfig:
    def __init__(self, config_file_path: str | Path) -> None:
        if isinstance(config_file_path, str):
            self.config_file_path = Path(config_file_path)
        if not self.config_file_path.exists():
            raise FileNotFoundError(f"There is no file with the given path!")
        self._config = self._set_config_from_file(self.config_file_path)

    def _set_config_from_file(self, config_file_path: str | Path) -> None:
        with open(config_file_path, 'r') as f:
            return yaml.load(f, Loader=yaml.Loader)
        
    def _set_source(self) -> DataSource | None:
        source_config: dict[str, Any] = self._config.get('source')
        if source_config.get('type') == 'email':
            source = EmailDataSource(config_file=source_config.get('config_file'))
            return source
        
    def _set_destination(self) -> DataDestination | None:
        destination_config: dict[str, Any] = self._config.get('destination')
        if destination_config.get('type') == 'file':
            destination = FileDataDestination(
                output_path=destination_config.get('output_path'),
                file_extension=destination_config.get('file_extension')
            )
            return destination


class BasePipeline(ABC):
    def __init__(
            self,
            pipeline_name: str,
            pipeline_source: DataSource | None = None,
            pipeline_destination: DataDestination | None = None,
            pipeline_config: PipelineConfig | None = None
    ) -> None:
        """Abstract Pipeline class. It should have `run`
        method as for running pipelines wtih given sources
        (extractors) and destinations (sinks/targets).

        Args:
            pipeline_name (str): _description_
            pipeline_source (DataSource): _description_
            pipeline_destination (DataDestination): _description_
            pipeline_config (PipelineConfig): _description_
        """
        self.name = pipeline_name
        if pipeline_config:
            self.config = pipeline_config
            self.source = pipeline_config._set_source()
            self.destination = pipeline_config._set_destination()
        elif (pipeline_source) and (pipeline_destination):
            self.source = pipeline_source
            self.destination = pipeline_destination
        else:
            raise ValueError("Couldn't create pipeline without config!")

    @abstractmethod
    def run(self) -> None:
        pass


class Pipeline(BasePipeline):
    """Basic pipeline implementation

    Args:
        BasePipeline (_type_): _description_
    """
    def __init__(
            self,
            pipeline_name: str,
            pipeline_source: DataSource | None = None,
            pipeline_destination: DataDestination | None = None,
            pipeline_config: PipelineConfig | None = None
    ) -> None:
        super().__init__(pipeline_name, pipeline_source, pipeline_destination, pipeline_config)

    def run(self, naive: bool = False) -> None:
        source = self.source
        destination = self.destination

        for data in source.extract(naive=naive):
            destination.load(data=data)


class PipelineOperator:
    def __init__(self) -> None:
        pass