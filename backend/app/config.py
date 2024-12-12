# this file contains all application configuration settings

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY= os.getenv('SECRET_KEY')

    # database configurations
    SQLALCHEMY_DATABASE_URI= os.getenv('DATABASE_URI', 'sqlite:///allomaison.db')
    SQLALCHEMY_TRACK_MODIFICATIONS= False

    # flask-mail configurations
    MAIL_SERVER= os.getenv('MAIL_SERVER')
    MAIL_PORT= os.getenv('MAIL_PORT')
    MAIL_USE_TLS= os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME= os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD= os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER= os.getenv('MAIL_DEFAULT_SENDER')

    # jwt configurations
    JWT_SECRET_KEY= os.getenv('JWT_SECRET_KEY')

    # cors configurations
    CORS_HEADERS= ['Content-Type', 'Authorization']
    CORS_ORIGINS= ['http://localhost:63343', 'http://127.0.0.1:63343']
    CORS_METHODS= ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_SUPPORTS_CREDENTIALS= True

class DevelopmentConfig(Config):
    DEBUG= True

class ProductionConfig(Config):
    DEBUG= False