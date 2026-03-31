from flask import current_app
from typing import Any

def register_socketio_handlers(socketio: Any, state) -> None:
    """
    Register Socket.IO event handlers.

    `state` is expected to provide `SessionLocal`.
    In this app, that is usually the database adapter.
    """
    @socketio.on("connect")
    def _handle_connect():
        current_app.logger.info("SocketIO client connected")

    @socketio.on("disconnect")
    def _handle_disconnect():
        current_app.logger.info("SocketIO client disconnected")
