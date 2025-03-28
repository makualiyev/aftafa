from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import (
    Mapped, mapped_column
)

from aftafa.client.odata.db import Base


class EntityType(Base):
    __tablename__ = 'enity_type'

    _id: Mapped[int] = mapped_column(Integer, name='id', primary_key=True)
    odata_server: Mapped[str] = mapped_column(String, name='odata_server', nullable=False)
    name: Mapped[str] = mapped_column(String, name='name', nullable=False)
    entity_type_name: Mapped[str] = mapped_column(String, name='entity_type_name', nullable=False)
    open_type: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f"OD_EntityType(entity_id={self._id!r}, name={self.name!r})"
