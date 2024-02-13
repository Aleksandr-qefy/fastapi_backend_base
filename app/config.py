import os

DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_USER = os.environ.get("DB_USER")
DB_SERVER = os.environ.get("DB_SERVER")
DB_NAME = os.environ.get("DB_NAME")

APP_NAME = "App"

APP_EMAIL_HOST = "some.anymail.com"
APP_EMAIL_PORT = 999
APP_EMAIL = "app@anymail.com"
APP_EMAIL_PASSWORD = "1234"

BACKEND_SERVER = "http://127.0.0.1:8000/"

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15

FRONTEND_CLIENT = "http://localhost:5000/"
