from flask import Flask
from flask_jwt_extended import JWTManager

from .utils.db_utils import bcrypt

from .routes.user_route import user
from .routes.product_route import product

app = Flask(__name__)

jwt = JWTManager()


def run_app(config):
    app.config.from_object(config)

    bcrypt.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(user)
    app.register_blueprint(product)
    return app
