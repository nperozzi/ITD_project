"""Persistence for payload delivery queue."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from adapters.types import TagId
from db.session import SessionFactory
from features.payload_delivery.schema import PayloadDeliveryRow
from features.payload_delivery.types import DeliveryState, PendingPayload
from logger import Logger


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PayloadDeliveryRepository:
    """CRUD over `payload_delivery` rows."""

    def __init__(
        self,
        session_factory: SessionFactory,
        logger: Logger | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._logger = logger or Logger("PayloadDeliveryRepository")

    def enqueue(self, tag_id: TagId, title: str, final_price: float) -> PendingPayload:
        with self._session_factory() as session:
            row = PayloadDeliveryRow(
                tag_id=tag_id,
                title=title,
                final_price=final_price,
                delivery_state=DeliveryState.PENDING,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._to_domain(row)

    def mark_delivering(self, payload_id: int) -> None:
        with self._session_factory() as session:
            row = session.get(PayloadDeliveryRow, payload_id)
            if row is None:
                return
            row.delivery_state = DeliveryState.DELIVERING
            row.attempt_count += 1
            row.last_attempted_at = _utc_now()
            session.commit()

    def mark_acknowledged(self, payload_id: int) -> None:
        with self._session_factory() as session:
            row = session.get(PayloadDeliveryRow, payload_id)
            if row is None:
                return
            row.delivery_state = DeliveryState.ACKNOWLEDGED
            session.commit()

    def mark_failed(self, payload_id: int) -> None:
        with self._session_factory() as session:
            row = session.get(PayloadDeliveryRow, payload_id)
            if row is None:
                return
            row.delivery_state = DeliveryState.FAILED
            session.commit()

    def reset_to_pending(self, payload_id: int) -> None:
        """Used after a transient failure so the next tick retries the payload."""

        with self._session_factory() as session:
            row = session.get(PayloadDeliveryRow, payload_id)
            if row is None:
                return
            row.delivery_state = DeliveryState.PENDING
            session.commit()

    def find_next_pending_for_tag(self, tag_id: TagId) -> PendingPayload | None:
        """Oldest pending payload for a tag. Older tags' obsolete payloads can be
        pruned by callers that only care about the latest.
        """

        with self._session_factory() as session:
            statement = (
                select(PayloadDeliveryRow)
                .where(PayloadDeliveryRow.tag_id == tag_id)
                .where(PayloadDeliveryRow.delivery_state == DeliveryState.PENDING)
                .order_by(PayloadDeliveryRow.created_at.asc())
                .limit(1)
            )
            row = session.execute(statement).scalar_one_or_none()
            return self._to_domain(row) if row is not None else None

    def list_pending(self) -> list[PendingPayload]:
        with self._session_factory() as session:
            statement = select(PayloadDeliveryRow).where(
                PayloadDeliveryRow.delivery_state.in_(
                    (DeliveryState.PENDING, DeliveryState.DELIVERING)
                )
            )
            return [
                self._to_domain(row)
                for row in session.execute(statement).scalars().all()
            ]

    def get(self, payload_id: int) -> PendingPayload | None:
        with self._session_factory() as session:
            row = session.get(PayloadDeliveryRow, payload_id)
            return self._to_domain(row) if row is not None else None

    @staticmethod
    def _to_domain(row: PayloadDeliveryRow) -> PendingPayload:
        return PendingPayload(
            id=row.id,
            tag_id=row.tag_id,
            title=row.title,
            final_price=row.final_price,
            delivery_state=row.delivery_state,
            attempt_count=row.attempt_count,
            last_attempted_at=row.last_attempted_at,
            created_at=row.created_at,
        )
