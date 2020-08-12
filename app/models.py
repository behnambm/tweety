from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
import time
from datetime import datetime


db = SQLAlchemy()

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    display_name = db.Column(db.String(50))
    bio = db.Column(db.String(160))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    avatar_path = db.Column(db.String, default='static/img/person.png')
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role',
                            secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    tweets = db.relationship('Tweet', backref='user', lazy='dynamic')


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweeted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(280), nullable=False)
    tweeted_at = db.Column(db.String(), default=time.time)
    likes = db.relationship('Like', backref='tweet', lazy='dynamic')
