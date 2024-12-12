from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import DevelopmentConfig
from argon2 import PasswordHasher
from flask_mail import Mail
from flask_cors import CORS
from .utils.validator import validate_environment

# define global instances
database= SQLAlchemy()
password_hasher= PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2
)
mail= Mail()

# application instance
def create_app():
    app= Flask(__name__)

    # loads app configurations from config.py
    app.config.from_object(DevelopmentConfig)

    # validate essential environment variables
    validate_environment([
        'JWT_SECRET_KEY',
        'BASE_URL',
        'MAIL_USERNAME',
        'CORS_ORIGINS',
        'CORS_HEADERS'
    ])

    # initialise global instances
    database.init_app(app)
    mail.init_app(app)

    # Initialize CORS with explicit configuration
    CORS(app,
         resources={r"/*":{
             'origins':app.config['CORS_ORIGINS'],
             'methods':app.config['CORS_METHODS'],
             'allow_headers':app.config['CORS_HEADERS'],
             'supports_credentials':app.config['CORS_SUPPORTS_CREDENTIALS']
         }})

    # register blueprints
    from app.routes.authentication import authentication_blueprint
    app.register_blueprint(authentication_blueprint)

    # create database from defined models
    with app.app_context():
        database.create_all()

    return app