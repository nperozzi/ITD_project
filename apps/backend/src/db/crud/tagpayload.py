from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.tagpayload import TagPayload


def create_tagpayload(
    db: Session,
    tag_id: int,
    payload_json: dict[str, Any],
    acknowledged: bool = False,
) -> TagPayload:
    tagpayload = TagPayload(
        tag_id=tag_id,
        payload_json=payload_json,
        acknowledged=acknowledged,
    )

    db.add(tagpayload)
    db.commit()
    db.refresh(tagpayload)

    return tagpayload


def get_tagpayload(db: Session, tagpayload_id: int) -> TagPayload | None:
    return db.get(TagPayload, tagpayload_id)


def get_all_tagpayloads(db: Session) -> list[TagPayload]:
    stmt = select(TagPayload)
    return db.scalars(stmt).all()


def get_latest_tagpayload_for_tag(db: Session, tag_id: int) -> TagPayload | None:
    stmt = select(TagPayload).where(TagPayload.tag_id == tag_id).order_by(TagPayload.id.desc())
    return db.scalars(stmt).first()


def get_latest_unacknowledged_tagpayload_for_tag(db: Session, tag_id: int) -> TagPayload | None:
    stmt = (
        select(TagPayload)
        .where(TagPayload.tag_id == tag_id, TagPayload.acknowledged.is_(False))
        .order_by(TagPayload.id.desc())
    )
    return db.scalars(stmt).first()


def update_tagpayload(db: Session, tagpayload_id: int, **kwargs: Any) -> TagPayload | None:
    tagpayload = db.get(TagPayload, tagpayload_id)
    if not tagpayload:
        return None

    for key, value in kwargs.items():
        if hasattr(tagpayload, key):
            setattr(tagpayload, key, value)

    db.commit()
    db.refresh(tagpayload)
    return tagpayload


def delete_tagpayload(db: Session, tagpayload_id: int) -> bool:
    tagpayload = db.get(TagPayload, tagpayload_id)
    if not tagpayload:
        return False

    db.delete(tagpayload)
    db.commit()
    return True
