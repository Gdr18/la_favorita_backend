import os

from dotenv import load_dotenv

load_dotenv(".env")

DATABASE_URI = os.getenv("MONGO_DB_URI")
GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DEFAULT_SENDER_EMAIL = os.getenv("DEFAULT_SENDER_EMAIL")


class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")


class DevelopmentConfig(Config):
    DEBUG = True


config = os.getenv("CONFIG")
