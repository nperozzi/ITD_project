from flask import current_app
from typing import Any
import random

def register_socketio_handlers(socketio: Any, state) -> None:
    """
    Register Socket.IO event handlers.

    `state` is expected to provide `get_tag(tag_id)`.
    In this app, that is usually the database adapter.
    """
    @socketio.on("connect")
    def _handle_connect():
        # Send initial battery value as soon as browser connects.
        current_app.logger.info("SocketIO client connected")
        # Keep battery generation on backend (frontend displays this value only).
        battery = random.randint(1, 100)
        if state:
            state.update_tag(1, 1, battery)
        socketio.emit("battery_update", {"battery": battery})

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")

    @socketio.on("request_battery")
    def _handle_request_battery():
        # Client manually requests current battery value from backend.
        battery = random.randint(1, 100)
        if state:
            state.update_tag(1, 1, battery)
        socketio.emit("battery_update", {"battery": battery})