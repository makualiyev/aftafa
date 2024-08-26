from typing import Optional

from sqlalchemy import String, Integer, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import (
    Mapped, mapped_column
)

from aftafa.client.ozon.db import Base


class CategoryTreeItem(Base):
    __tablename__ = 'category_tree_item'

    _id: Mapped[int] = mapped_column(Integer, name='_id', primary_key=True, autoincrement=True, nullable=False)
    # _parent_id: Mapped[Optional[int]] = mapped_column(
    #     Integer, ForeignKey("category_tree_item.description_category_id"), name='_parent_id', nullable=True
    # )
    _parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, name='_parent_id', nullable=True
    )
    description_category_id: Mapped[int] = mapped_column(Integer, name='description_category_id', nullable=True)
    category_name: Mapped[Optional[str]] = mapped_column(String(100), name='category_name', nullable=True)
    disabled: Mapped[bool] = mapped_column(Boolean, name='disabled', nullable=False)
    type_id: Mapped[Optional[int]] = mapped_column(Integer, name='type_id', nullable=True)
    type_name: Mapped[Optional[str]] = mapped_column(String(100), name='type_name', nullable=True)

    def __repr__(self) -> str:
        return f"OZ_CategoryTreeItem(descr_category_id={self.description_category_id!r}, name={self.category_name!r})"
