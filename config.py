import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///finpath.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
