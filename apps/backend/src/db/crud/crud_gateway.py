
from typing import Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import DateTime, select
from db.models.gateway import Gateway, Status

def create_gateway(db: Session, status: Status, store_id: Optional[int] = None, 
                   last_heartbeat_at: Optional[DateTime] = None,
                   ) -> Gateway:
    gateway = Gateway (store_id=store_id, status=status, 
                       last_heartbeat_at=last_heartbeat_at)

    db.add(gateway)
    db.commit()
    db.refresh(gateway)
    return gateway

def get_gateway(db: Session, gateway_id: int) -> Gateway | None:
    return db.get(Gateway, gateway_id)

def get_all_gateways(db: Session):
    gateways = select(Gateway)
    return db.scalars(gateways).all()

def update_gateway(db: Session, gateway_id: int, **kwargs: Any) -> Gateway | None:
    gateway = db.get(Gateway, gateway_id)

    if not gateway:
        return None
    
    for key, value in kwargs.items():
        if hasattr(gateway, key):
            setattr(gateway, key, value)
    
    db.commit()
    db.refresh(gateway)

    return gateway

def delete_gateway(db: Session, gateway_id: int) -> bool:
    gateway = db.get(Gateway, gateway_id)

    if not gateway:
        return False
    
    db.delete(gateway)
    db.commit()

    return True
