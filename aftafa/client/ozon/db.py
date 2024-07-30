from datetime import datetime
from typing import Any

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# DeclarativeBase = declarative_base()

class Base(DeclarativeBase):
    # __tablename__ = 'xtest'

    _stl_extracted_at: Mapped[datetime] = mapped_column(name='_stl_extracted_at', nullable=False)


class FakeBase(DeclarativeBase):
    # __tablename__ = 'xtest'
    # def __init__(self, **kw: Any):
    #     super().__init__(**kw)
    __table_args__ = {
        'schema': 'moysklad'
    }

    _stl_extracted_at: Mapped[datetime] = mapped_column(name='_stl_extracted_at', nullable=False)
