from flask import Flask
from flask_socketio import SocketIO
from routes import api
from mqtt_client import start, set_app_and_socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(api)

# Pass app and socketio instances to mqtt_client
set_app_and_socketio(app, socketio)

def main():
    start()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()