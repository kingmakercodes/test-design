from datetime import timezone, datetime
from app import password_hasher
from app import database

class BaseUser(database.Model):
    __abstract__= True

    id= database.Column(database.Integer, primary_key=True)
    name= database.Column(database.String(80), nullable=False)
    surname= database.Column(database.String(80), nullable=False)
    email= database.Column(database.String(100), unique=True, nullable=False)

    created_at= database.Column(database.DateTime, default=datetime.now(timezone.utc))


class PendingUser(BaseUser):
    __tablename__='pending_user'

    id= database.Column(database.Integer, primary_key=True)
    password= database.Column(database.String(80), nullable=False)


class RegisteredUser(BaseUser):
    __abstract__=True

    id= database.Column(database.Integer, primary_key=True)
    password_hash= database.Column(database.String(150), nullable=False)

    user_type= database.Column(database.String(80), nullable=False) # discriminator column
    is_service_renderer= database.Column(database.Boolean, default=False)

    __mapper_args__= {
        'polymorphic_identity': 'registered_user',  # base identifier
        'polymorphic_on': user_type
    }

    # hash password function
    def set_password(self, password):
        self.password_hash= password_hasher.hash(password)

    def check_password(self, password):
        return password_hasher.verify(self.password_hash, password)


class Client(RegisteredUser):
    __tablename__='client'

    id= database.Column(database.Integer, primary_key=True)
    __mapper_args__={
        'polymorphic_identity': 'client'
    }


class Servicer(RegisteredUser):
    __tablename__='service_renderer'

    id= database.Column(database.Integer, primary_key=True)
    __mapper_args__={
        'polymorphic_identity': 'service_renderer'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # call the parent constructor, Registered User, to define other attributes to this class
        self.is_service_renderer= True  # ensures this is always True for Servicer