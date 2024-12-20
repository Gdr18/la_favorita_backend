from flask import Flask

from src.routes.auth_route import auth_route
from src.routes.email_tokens_route import email_tokens_route
from src.routes.products_route import products_route
from src.routes.refresh_tokens_route import refresh_tokens_route
from src.routes.revoked_tokens_route import revoked_tokens_route
from src.routes.settings_route import settings_route
from src.routes.users_route import users_route
from src.services.security_service import jwt, oauth, bcrypt

app = Flask(__name__)


def run_app(config):
    app.config.from_object(config)

    bcrypt.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)

    app.register_blueprint(users_route, url_prefix="/users")
    app.register_blueprint(products_route, url_prefix="/products")
    app.register_blueprint(settings_route, url_prefix="/settings")
    app.register_blueprint(auth_route, url_prefix="/auth")
    app.register_blueprint(revoked_tokens_route, url_prefix="/revoked-tokens")
    app.register_blueprint(refresh_tokens_route, url_prefix="/refresh-tokens")
    app.register_blueprint(email_tokens_route, url_prefix="/email-tokens")

    return app
