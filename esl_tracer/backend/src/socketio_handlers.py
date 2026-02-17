from flask import current_app
from typing import Any

def register_socketio_handlers(socketio: Any, state) -> None:
    """
    Register Socket.IO event handlers.
    """
    @socketio.on("connect")
    def _handle_connect():
        current_app.logger.info("SocketIO client connected")
        socketio.emit("battery_update", {"battery": getattr(state, "latest_battery", None)})

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")

    @socketio.on("request_battery")
    def _handle_request_battery():
        """Client asks for current battery value."""
        socketio.emit("battery_update", {"battery": getattr(state, "latest_battery", None)})