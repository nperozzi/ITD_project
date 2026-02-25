from database import BackendDB
from flask import Flask
from flask_socketio import SocketIO
from routes import api
from socketio_handlers import register_socketio_handlers
from mqtt_client import mqtt_client_connect, set_app, set_socketio, set_db
import database

def main():
    # Init database
    db = BackendDB()

    # Creates Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['db'] = db

    #Registers the Blueprint
    app.register_blueprint(api)

    #Initializes SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    register_socketio_handlers(socketio, database)
    register_socketio_handlers(socketio, db)

    # Pass app and socketio instances to mqtt_client.py
    set_app(app)
    set_socketio(socketio)
    set_db(db)

    mqtt_client_connect()   
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()
