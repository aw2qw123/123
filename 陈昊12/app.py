from flask import Flask
import os

from config import Config
from user.__init__ import user_ap
from util.middlewares import jwt_authentication

app = Flask(__name__)
app.register_blueprint(user_ap)
app.secret_key = os.urandom(24)
app.config.from_object(Config)
app.before_request(jwt_authentication)
if __name__ == '__main__':
    app.run()
