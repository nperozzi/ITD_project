from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.crud.crud_tagpayload import get_all_tagpayloads
from db.models.tagpayload import TagPayload


def tagpayload_to_dictionary(tagpayload: TagPayload) -> dict[str, Any]:
    return {
        "id": tagpayload.id,
        "payloadJson": tagpayload.payload_json,
    }


def list_all_tagpayloads(db: Session) -> list[dict[str, Any]]:
    return [tagpayload_to_dictionary(tagpayload) for tagpayload in get_all_tagpayloads(db)]
