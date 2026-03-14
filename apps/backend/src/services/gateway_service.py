from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from db.crud.crud_gateway import create_gateway, delete_gateway, get_all_gateways, get_gateway, update_gateway
from db.models.gateway import Gateway, Status


class GatewayValidationError(ValueError):
    """Raised when incoming gateway payloads are invalid."""


def convert_gateway_obj_to_dict(gateway: Gateway) -> dict[str, Any]:
    return {
        "id": gateway.id,
        "storeId": gateway.store_id,
        "status": _convert_status_obj_to_str(gateway.status),
        "lastHeartbeatAt": gateway.last_heartbeat_at.isoformat() + "Z" if gateway.last_heartbeat_at else "",
    }


def list_all_gateways(db: Session) -> list[dict[str, Any]]:
    return [convert_gateway_obj_to_dict(gateway) for gateway in get_all_gateways(db)]


def get_gateway_details(db: Session, gateway_id: int) -> dict[str, Any] | None:
    gateway = get_gateway(db, gateway_id)
    if gateway is None:
        return None
    return convert_gateway_obj_to_dict(gateway)


def create_gateway_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    gateway_data = _validated_gateway_fields(payload, partial=False)
    gateway = create_gateway(db=db, **gateway_data)
    return convert_gateway_obj_to_dict(gateway)


def update_gateway_from_payload(db: Session, gateway_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    gateway_data = _validated_gateway_fields(payload, partial=True)
    if not gateway_data:
        raise GatewayValidationError("At least one updatable field is required.")

    gateway = update_gateway(db, gateway_id, **gateway_data)
    if gateway is None:
        return None
    return convert_gateway_obj_to_dict(gateway)


def delete_gateway_by_id(db: Session, gateway_id: int) -> bool:
    return delete_gateway(db, gateway_id)


def _validated_gateway_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GatewayValidationError("JSON object payload is required.")

    allowed_fields = {"storeId", "status", "lastHeartbeatAt"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise GatewayValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "storeId" in payload:
        data["store_id"] = _validate_optional_int(payload["storeId"], "storeId")

    if "status" in payload:
        data["status"] = _convert_status_str_to_obj(payload["status"])
    elif not partial:
        raise GatewayValidationError("Field 'status' is required.")

    if "lastHeartbeatAt" in payload:
        data["last_heartbeat_at"] = _validate_datetime(payload["lastHeartbeatAt"])

    return data


def _validate_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise GatewayValidationError(f"Field '{field_name}' must be an integer or null.")
    if value <= 0:
        raise GatewayValidationError(f"Field '{field_name}' must be greater than 0.")
    return value


def _validate_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise GatewayValidationError("Field 'lastHeartbeatAt' must be an ISO 8601 string or null.")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1]
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise GatewayValidationError("Field 'lastHeartbeatAt' must be an ISO 8601 string or null.") from exc


def _convert_status_str_to_obj(value: Any) -> Status:
    if not isinstance(value, str):
        raise GatewayValidationError("Field 'status' must be a string.")

    normalized = value.strip().lower()
    if normalized == "online":
        return Status.ONLINE
    if normalized == "offline":
        return Status.OFFLINE
    if normalized in {"degraded", "disabled"}:
        return Status.DISABLED

    raise GatewayValidationError("Field 'status' must be one of: online, offline, degraded.")


def _convert_status_obj_to_str(status: Status) -> str:
    if status is Status.DISABLED:
        return "degraded"
    return status.value
