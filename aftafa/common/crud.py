"""General module for CRUD based operations.
"""
from datetime import datetime
from typing import Generic, TypeVar, Any

from sqlalchemy import Engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.orm.decl_api import DeclarativeBase
from pydantic import BaseModel


class CRUDWriter:
    """
    """
    def __init__(
                self,
                _session: Session,
                database_model: DeclarativeBase,
                pydantic_model: BaseModel | None,
                extraction_ts: datetime | None = None
        ) -> None:
        self.db_session = _session
        self.database_model = database_model
        self.pydantic_model = pydantic_model
        self.filter_criteria = []
        if extraction_ts:
            self.extraction_ts = extraction_ts
        else:
            self.extraction_ts = datetime.now()

    def _query_model(self, **kwargs) -> DeclarativeBase:
        return self.db_session.query(self.database_model).filter_by(**kwargs)
    
    def _set_filter_criteria(self, database_model: DeclarativeBase) -> dict[str, Any]:
        criteria_repr: dict[str, Any] = {}
        for criteria in self.filter_criteria:
            criteria_repr[criteria] = getattr(database_model, criteria)
        return criteria_repr

    def prepare_model(
            self,
            schema: dict[str, str],
            normalized: bool = False,
            by_alias: bool = False,
            **kwargs
        ) -> DeclarativeBase:
        if normalized:
            schema = self.pydantic_model(**schema)._t_normalize(by_alias=by_alias)
        else:
            schema = self.pydantic_model(**schema).dict(by_alias=by_alias)
        req_fields: list[str] = [i for i in self.database_model.__dict__ if not i.startswith('_')]
        schema['extracted_at'] = self.extraction_ts
        if kwargs:
            for key, value in kwargs.items():
                schema[key] = value
        schema = {key: value for key, value in schema.items() if key in req_fields}
        return self.database_model(**schema)

    def check_integrity(self, database_model: DeclarativeBase) -> bool:
        kwargs = self._set_filter_criteria(database_model=database_model)
        model_in_db: self.database_model = self._query_model(**kwargs).first()
        if model_in_db:
            return True
        return False

    def update(self, database_model: DeclarativeBase) -> int:
        kwargs = self._set_filter_criteria(database_model=database_model)
        database_model_in_db: self.database_model = self._query_model(**kwargs).first()
        for attr_k, attr_v in database_model.__dict__.items():
             if not attr_k.startswith('_'):
                 setattr(database_model_in_db, attr_k, attr_v)
        self.db_session.commit()
        if hasattr(database_model_in_db, 'id'):
            return database_model_in_db.id
        return 0

    def create(self, database_model: DeclarativeBase) -> int:
        self.db_session.add(database_model)
        self.db_session.commit()
        if hasattr(database_model, 'id'):
            return database_model.id
        return 0
    
    def bulk_create(self) -> None:
        pass
    
    def refresh(self, schema: dict[str, str], return_id: bool = False) -> None:
        database_model: DeclarativeBase = self.prepare_model(schema=schema)
        if self.check_integrity(database_model=database_model):
            database_model_id: int = self.update(database_model=database_model)
            if return_id:
                return database_model_id
            return None
        database_model_id: int = self.create(database_model=database_model)
        if return_id:
            return database_model_id
        return None
    