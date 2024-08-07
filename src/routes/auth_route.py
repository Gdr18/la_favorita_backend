from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required


from ..utils.db_utils import db, bcrypt

auth = Blueprint("auth", __name__)

coll_users = db.users


@auth.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    try:
        user_request = coll_users.find_one({"email": data["email"]})
        # TODO: Refactorizar
        if user_request:
            if bcrypt.check_password_hash(user_request["password"], data["password"]):
                access_token = create_access_token(
                    identity={"id": str(user_request["_id"]), "role": user_request["role"]}
                )
                return jsonify(access_token=access_token), 200
            else:
                return jsonify(err="Error: La contraseña no coincide"), 401
        else:
            return jsonify(err="Error: El usuario no ha sido encontrado"), 404
    except Exception as e:
        return jsonify(err=f"Error: {e}"), 500


@auth.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    pass
