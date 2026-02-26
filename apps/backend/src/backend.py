"""Application entry point for the backend service.

This module wires together:
- SQLite data access
- Flask HTTP routes
- Socket.IO realtime updates
- MQTT client integration
"""

from database import BackendDB
from flask import Flask
from flask_socketio import SocketIO
from routes import api
from socketio_handlers import register_socketio_handlers
from mqtt_client import mqtt_client_connect, set_app, set_socketio, set_db
import database

def main():
    # 1) Initialize database state.
    db = BackendDB()

    # 2) Create Flask app and attach shared objects to config.
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['db'] = db

    # 3) Register API routes.
    app.register_blueprint(api)

    # 4) Initialize Socket.IO for realtime browser updates.
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Register socket event handlers.
    # (Current codebase uses two calls; behavior is unchanged.)
    register_socketio_handlers(socketio, database)
    register_socketio_handlers(socketio, db)

    # 5) Share app/socket/db with MQTT module.
    set_app(app)
    set_socketio(socketio)
    set_db(db)

    # 6) Connect to MQTT broker and start web server.
    mqtt_client_connect()   
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()
