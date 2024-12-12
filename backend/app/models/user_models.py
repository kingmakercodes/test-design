from app import database, password_hasher
from datetime import datetime, timedelta, timezone


class BaseUser(database.Model):
    __abstract__=True

    id= database.Column(database.Integer, primary_key=True)
    name= database.Column(database.String(80), nullable=False)
    surname= database.Column(database.String(80), nullable=False)
    email= database.Column(database.String(100), unique=True, nullable=False)

    created_at= database.Column(database.DateTime, default=datetime.now(timezone.utc))


class PendingUser(BaseUser):
    __tablename__='pending_user'

    password= database.Column(database.String(128), nullable=False)


class RegisteredUser(BaseUser):
    __tablename__='registered_users'

    password_hash= database.Column(database.String(128))

    # hash password function
    def set_password(self, password):
        self.password_hash= password_hasher.hash(password)

    def check_password(self, password):
        return password_hasher.verify(self.password_hash, password)