from typing import TypeVar, Generic

from fastapi import Header, HTTPException
from pydantic import Field
from pydantic.generics import GenericModel


class PaginationParams:
    def __init__(self, offset: int = 0, limit: int = 100):
        self.offset = offset
        self.limit = limit


T = TypeVar('T')


class PaginationResponse(GenericModel, Generic[T]):
    offset: int = Field(example=0)
    limit: int = Field(example=100)
    total: int = Field(example=1)
    items: list[T]
