"""Pydantic inputs for payload delivery."""

from __future__ import annotations

from pydantic import BaseModel, Field

from adapters.types import TagId


class EnqueuePayloadInput(BaseModel):
    """A new payload arriving from the backend."""

    tag_id: TagId = Field(ge=1)
    title: str = Field(min_length=1, max_length=127)
    final_price: float = Field(ge=0)
