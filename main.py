from flask import Flask
from db.models import Device, Location, Interaction
from routes.phone_routes import phone_blueprint

app = Flask(__name__)


if __name__ == '__main__':
   app.register_blueprint(phone_blueprint)
   app.run(port=5000)
