from bson import ObjectId
from flask import Blueprint, request, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt, decode_token
from pydantic import ValidationError
from pymongo import errors, ReturnDocument

from src.models.token_model import TokenModel
from src.models.user_model import UserModel
from src.services.db_services import db
from src.services.email_service import send_email
from src.services.security_service import (
    generate_access_token,
    generate_refresh_token,
    revoke_access_token,
    delete_refresh_token,
    google,
    bcrypt,
)
from src.utils.exceptions_management import (
    handle_unexpected_error,
    ClientCustomError,
    handle_duplicate_key_error,
    handle_validation_error,
)
from src.utils.successfully_responses import resource_msg

auth_route = Blueprint("auth", __name__)


@auth_route.route("/auth/login", methods=["POST"])
def login():
    try:
        user_data = request.get_json()
        user_requested = db.users.find_one({"email": user_data.get("email")})
        if user_requested:
            if bcrypt.check_password_hash(user_requested.get("password"), user_data.get("password")):
                if user_requested.get("confirmed"):
                    access_token = generate_access_token(user_requested)
                    refresh_token = generate_refresh_token(user_requested)
                    return (
                        jsonify(
                            msg=f"El usuario '{user_requested.get('_id')}' ha iniciado sesión de forma manual",
                            access_token=access_token,
                            refresh_token=refresh_token,
                        ),
                        200,
                    )
                else:
                    raise ClientCustomError("not_confirmed")
            else:
                raise ClientCustomError("not_match")
        else:
            raise ClientCustomError("not_found", "usuario")
    except ClientCustomError as e:
        return e.response
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    token = get_jwt()
    try:
        revoked_token = revoke_access_token(token)
        delete_refresh_token(token["sub"])
        return revoked_token
    except errors.DuplicateKeyError as e:
        return handle_duplicate_key_error(e)
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/login/google")
def login_google():
    try:
        redirect_uri = url_for("auth.authorize_google", _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/google")
def authorize_google():
    try:
        google_token = google.authorize_access_token()
        nonce = request.args.get("nonce")
        google_user_info = google.parse_id_token(google_token, nonce=nonce)

        user_data = {"name": google_user_info.get("name"), "auth_provider": "google", "confirmed": True}

        user = db.users.find_one_and_update(
            {"email": google_user_info.get("email")},
            {"$set": user_data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        return (
            jsonify(
                {
                    "msg": f"""El usuario '{user.get("_id")}' ha iniciado sesión con Google""",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            200,
        )
    except errors.DuplicateKeyError as e:
        return handle_duplicate_key_error(e)
    except ValidationError as e:
        return handle_validation_error(e)
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/refresh")
@jwt_required(refresh=True)
def refresh_users_token():
    try:
        user_id = get_jwt().get("sub")
        check_refresh_token = TokenModel.get_refresh_token_by_user_id(user_id)
        if check_refresh_token:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            access_token = generate_access_token(user_data)
            return jsonify(access_token=access_token, msg="El token de acceso se ha generado"), 200
        else:
            raise ClientCustomError("not_found", "refresh_token")
    except ClientCustomError as e:
        return e.response
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/confirm_email/<token>", methods=["GET"])
def confirm_email(token):
    try:
        user_identity = decode_token(token)
        user_id = user_identity.get("sub")
        user_requested = db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
        if user_requested:
            user_requested["confirmed"] = True
            user_object = UserModel(**user_requested)
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_object.to_dict()})
            return resource_msg(user_id, "usuario", "confirmado")
        else:
            raise ClientCustomError("not_found", "usuario")
    except ClientCustomError as e:
        return e.response
    except Exception as e:
        return handle_unexpected_error(e)


@auth_route.route("/auth/resend_email/<user_id>", methods=["POST"])
def resend_email(user_id):
    try:
        user_token = TokenModel.get_email_tokens_by_user_id(user_id)
        if len(user_token) < 5:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                send_email(user_data)
                return resource_msg(user_id, "email de confirmación", "reenviado")
            else:
                raise ClientCustomError("not_found", "usuario")
        else:
            raise ClientCustomError("too_many_requests")
    except ClientCustomError as e:
        return e.response
    except Exception as e:
        return handle_unexpected_error(e)
