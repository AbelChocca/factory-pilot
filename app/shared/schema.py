from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]

    total_items: int

    total_pages: int

    current_page: int