from dotenv import load_dotenv
import os

load_dotenv(".env")

database = os.getenv("MONGO_DB_URI")


class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 3600


class DevelopmentConfig(Config):
    DEBUG = True


config = os.getenv("CONFIG")
