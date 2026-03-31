from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.tag import Status, Tag


def _normalize_status(status: Status | str) -> Status:
    if isinstance(status, Status):
        return status

    if isinstance(status, str):
        lowered = status.strip().lower()
        for enum_value in Status:
            if enum_value.value == lowered:
                return enum_value

    raise ValueError(f"Invalid status: {status}")


def _validate_battery_pct(battery_pct: Optional[int]) -> None:
    if battery_pct is None:
        return
    if not 0 <= battery_pct <= 100:
        raise ValueError("battery_pct must be between 0 and 100")


def create_tag(db: Session, status: Status | str, 
    battery_pct: Optional[int] = None, product_id: Optional[int] = None,
    shelf_location_id: Optional[int] = None,) -> Tag:

    normalized_status = _normalize_status(status)
    _validate_battery_pct(battery_pct)

    tag = Tag(
        battery_pct = battery_pct,
        status = normalized_status,
        product_id = product_id,
        shelf_location_id = shelf_location_id,
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return db.get(Tag, tag_id)


def get_all_tags(db: Session):
    tags = select(Tag)
    return db.scalars(tags).all()


def update_tag(db: Session, tag_id: int, **kwargs: Any) -> Tag | None:
    tag = db.get(Tag, tag_id)

    if not tag:
        return None

    if "status" in kwargs:
        kwargs["status"] = _normalize_status(kwargs["status"])
    if "battery_pct" in kwargs:
        _validate_battery_pct(kwargs["battery_pct"])

    for key, value in kwargs.items():
        if hasattr(tag, key):
            setattr(tag, key, value)

    db.commit()
    db.refresh(tag)

    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    tag = db.get(Tag, tag_id)

    if not tag:
        return False

    db.delete(tag)
    db.commit()

    return True
