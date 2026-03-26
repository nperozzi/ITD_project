from flask import current_app
from typing import Any
import random
from db.crud.tag import update_tag

def register_socketio_handlers(socketio: Any, state) -> None:
    """
    Register Socket.IO event handlers.

    `state` is expected to provide `SessionLocal`.
    In this app, that is usually the database adapter.
    """
    @socketio.on("connect")
    def _handle_connect():
        # Send initial battery value as soon as browser connects.
        current_app.logger.info("SocketIO client connected")
        # Keep battery generation on backend (frontend displays this value only).
        battery = random.randint(1, 100)
        if state:
            with state.SessionLocal() as session:
                update_tag(session, 1, product_id=1, battery_pct=battery)
        socketio.emit("battery_update", {"battery": battery})

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")

    @socketio.on("request_battery")
    def _handle_request_battery():
        # Client manually requests current battery value from backend.
        battery = random.randint(1, 100)
        if state:
            with state.SessionLocal() as session:
                update_tag(session, 1, product_id=1, battery_pct=battery)
        socketio.emit("battery_update", {"battery": battery})
