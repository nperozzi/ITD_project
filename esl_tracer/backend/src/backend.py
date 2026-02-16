from flask import Flask
from routes import api
from mqtt_client import start

app = Flask(__name__)
app.register_blueprint(api)

def main():
    start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()