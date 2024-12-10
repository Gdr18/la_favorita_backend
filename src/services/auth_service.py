from datetime import timedelta

from authlib.integrations.flask_client import OAuth
from flask import jsonify, Response
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager, decode_token

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from ..models.token_model import TokenModel
from ..utils.db_utils import db
from ..utils.successfully_responses import resource_msg

jwt = JWTManager()
oauth = OAuth()

google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def generate_access_token(user_data: dict) -> str:
    user_role = user_data.get("role")
    user_identity = user_data.get("_id")

    token_info = {
        "identity": str(user_identity),
        "additional_claims": {"role": user_role},
        "expires_delta": get_expiration_time_access_token(user_role),
    }

    access_token = create_access_token(**token_info)

    return access_token


def generate_refresh_token(user_data: dict) -> str:
    user_role = user_data.get("role")
    user_identity = user_data.get("_id")

    token_info = {"identity": str(user_identity), "expires_delta": get_expiration_time_refresh_token(user_role)}
    refresh_token = create_refresh_token(**token_info)

    refresh_token_decoded = decode_token(refresh_token)
    data_refresh_token_db = {
        "user_id": refresh_token_decoded.get("sub"),
        "jti": refresh_token_decoded.get("jti"),
        "expires_at": refresh_token_decoded.get("exp"),
    }
    response = TokenModel(**data_refresh_token_db).insert_refresh_token()

    if response:
        return refresh_token
    else:
        raise Exception("Error al guardar el refresh token en la base de datos")


def generate_email_token(user_data: dict) -> str:
    user_identity = user_data.get("_id")

    token_info = {"identity": str(user_identity), "expires_delta": timedelta(days=1)}

    email_token = create_access_token(**token_info)

    return email_token


def get_expiration_time_access_token(role: int) -> timedelta:
    if role == 1:
        return timedelta(minutes=15)
    elif role == 2:
        return timedelta(hours=3)
    else:
        return timedelta(days=1)


def get_expiration_time_refresh_token(role: int) -> timedelta:
    if role == 1:
        return timedelta(hours=3)
    elif role == 2:
        return timedelta(hours=6)
    else:
        return timedelta(days=30)


# TODO: Eliminar esta función cuando se refactorice token_model.py
def revoke_token(token: dict) -> tuple[Response, int]:
    token_jti = token.get("jti")
    token_exp = token.get("exp")
    token_sub = token.get("sub")
    token_object = TokenModel(user_id=token_sub, jti=token_jti, expires_at=token_exp)
    token_revoked = db.revoked_tokens.insert_one(token_object.to_dict())
    return resource_msg(token_revoked.inserted_id, "token revocado", "añadido", 201)


# TODO: Comprobar si esto es más seguro y no afecta mucho al rendimiento. En vez de meter el rol en el token, se puede hacer una consulta a la base de datos.
# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_headers, jwt_data):
#     user_id = jwt_data["sub"]
#     return db.users.find_one({"_id": user_id})

# Prueba de rendimiento
# import time
# start_time = time.time()
# your_function()
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Tiempo de ejecución: {execution_time} segundos")


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
    return jsonify(err="Necesita un token válido para acceder a esta ruta"), 401
