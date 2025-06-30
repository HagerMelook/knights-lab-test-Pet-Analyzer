from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

#initializes the SQLAlchemy object
db = SQLAlchemy()

#initializes the Bcrypt object, used for secure password hashing
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.String(200), default='default.png')

    # generate the password hash
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # check whether the input password will match the password hash for that user after hashing or not
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
