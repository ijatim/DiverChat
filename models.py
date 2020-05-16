from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(50))
    phone_number = db.Column(db.Integer(), unique=True)
    password = db.Column(db.String(50))
