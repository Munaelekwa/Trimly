from utils import db
from flask_login import UserMixin
from datetime import datetime



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    links = db.relationship('Link', backref='user', lazy=True)
    qr_codes = db.relationship('Qrcode', backref='user', lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_url = db.Column(db.String(2000), nullable=False)
    shortened_url = db.Column(db.String(15), unique=True, nullable=False)
    custom_url = db.Column(db.String(15), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    title = db.Column(db.String(15), default='Untitled')
    clicks = db.Column(db.Integer(), default=0)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Qrcode(db.Model):
    id = db.Column(db.Integer() , primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(2000), nullable=False)
    title = db.Column(db.String(15), default='Untitled')
    scans = db.Column(db.Integer(), default=0)
    code = db.Column(db.String(15), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()









