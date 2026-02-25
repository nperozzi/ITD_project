from flask import current_app
from typing import Any

def register_socketio_handlers(socketio: Any, state) -> None:
    """
    Register Socket.IO event handlers.
    """
    @socketio.on("connect")
    def _handle_connect():
        current_app.logger.info("SocketIO client connected")
        tag = state.get_tag(1) if state else None
        battery = tag["battery_level"] if tag else None
        socketio.emit("battery_update", {"battery": battery})

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")

    @socketio.on("request_battery")
    def _handle_request_battery():
        """Client asks for current battery value."""
        tag = state.get_tag(1) if state else None
        battery = tag["battery_level"] if tag else None
        socketio.emit("battery_update", {"battery": battery})