from flask import Flask
from flask_socketio import SocketIO
from routes import api
from socketio_handlers import register_socketio_handlers
from mqtt_client import mqtt_client_connect, set_app, set_socketio
import state

# Creates Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

#Initializes SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
register_socketio_handlers(socketio, state)

#Registers the Blueprint
app.register_blueprint(api)

# Pass app and socketio instances to mqtt_client.py
set_app(app)
set_socketio(socketio)

def main():
    mqtt_client_connect()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()