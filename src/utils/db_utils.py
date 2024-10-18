from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from config import database_uri


def db_connection() -> Database:
    try:
        client = MongoClient(database_uri)
        database = client["test_la_favorita"]
        return database
    except ConnectionFailure:
        print("No se pudo conectar a la base de datos")


# Instancias necesarias para la conexión a la base de datos, el cifrado de contraseñas y autenticación JWT
db = db_connection()
bcrypt = Bcrypt()
jwt = JWTManager()
