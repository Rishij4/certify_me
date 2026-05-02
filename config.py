import os

class Config:
    SECRET_KEY = "secret123"

    uri = os.getenv("DATABASE_URL")

    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri or "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False