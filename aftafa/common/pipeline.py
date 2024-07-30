from abc import ABC, abstractmethod

from aftafa.common.resource import Resource
from aftafa.common.loader import Loader


class BasePipeline(ABC):
    def __init__(
            self,
            name: str,
            resource: Resource,
            loader: Loader
    ) -> None:
        """Abstract Pipeline class. It should have 
        `run` method as for running pipelines wtih
        given resources (extractors) and loaders (sinks/
        targets)"""
        self.name = name
        self.resource = resource
        self.loader = loader

    @abstractmethod
    def run(self) -> None:
        pass


class Pipeline(BasePipeline):
    def __init__(
            self,
            name: str,
            resource: Resource,
            destination: Loader
    ) -> None:
        """Basic Pipeline implementation.
        """
        super().__init__(
            name,
            resource,
            destination
        )

    def run(self, naive: bool = False) -> None:
        resource = self.resource
        loader = self.loader
        data = resource.extract(naive=naive)

        
        if not data:
            print(f'Pipeline \'{self.name}\' failed')
        
        loader.load(data=data)


class PipelineOperator:
    def __init__(self) -> None:
        pass