from datetime import timedelta

from authlib.integrations.flask_client import OAuth
from flask import jsonify
from flask_jwt_extended import create_access_token, JWTManager

from config import google_client_id, google_client_secret
from ..models.revoked_token_model import RevokedTokenModel
from ..utils.db_utils import db
from ..utils.successfully_responses import resource_msg

jwt = JWTManager()
oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=google_client_id,
    client_secret=google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def generate_token(user_data, time):
    access_token = create_access_token(
        identity=str(user_data.get("_id")),
        additional_claims={"role": user_data.get("role")},
        expires_delta=timedelta(minutes=time),
    )
    # TODO: Crear un token de refresco y guardarlo en la base de datos.
    return access_token


def revoke_token(token_jti, token_exp):
    token_object = RevokedTokenModel(jti=token_jti, exp=token_exp)
    token_revoked = db.revoked_tokens.insert_one(token_object.to_dict())
    return resource_msg(token_revoked.inserted_id, "token revocado", "añadido", 201)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    check_token = db.revoked_tokens.find_one({"jti": jwt_payload.get("jti")})
    return True if check_token else None


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify(err="El token ha sido revocado"), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify(err="El token ha expirado"), 401


@jwt.unauthorized_loader
def unauthorized_callback(error_message):
    return jsonify(err="Necesita un token autorizado para acceder a esta ruta"), 401
