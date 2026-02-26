from flask import current_app
from typing import Any

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
        tag = state.get_tag(1) if state else None
        battery = tag["battery_level"] if tag else None
        socketio.emit("battery_update", {"battery": battery})

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")

    @socketio.on("request_battery")
    def _handle_request_battery():
        # Client manually requests current battery value.
        tag = state.get_tag(1) if state else None
        battery = tag["battery_level"] if tag else None
        socketio.emit("battery_update", {"battery": battery})