from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
import time
from datetime import datetime


db = SQLAlchemy()

roles_users = db.Table('tweety__roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('tweety__user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('tweety__role.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = 'tweety__role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


user_follow = db.Table(
    'tweety__user_follow',
    db.Column('follower_id', db.Integer, db.ForeignKey('tweety__user.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('tweety__user.id'))
)


class Bookmark(db.Model):
    __tablename__ = 'tweety__bookmark'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tweety__user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweety__tweet.id'))
    created_at = db.Column(db.String, default=time.time)


class User(db.Model, UserMixin):
    __tablename__ = 'tweety__user'
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
    followings = db.relationship(
        'User',
        secondary=user_follow,
        primaryjoin=(user_follow.c.follower_id == id),
        secondaryjoin=(user_follow.c.following_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')

    def i_follow(self, user):
        return self.followings.filter(
            user_follow.c.following_id == user.id
        ).count() > 0

    def follow(self, user):
        if not self.i_follow(user):
            self.followings.append(user)

    def unfollow(self, user):
        if self.i_follow(user):
            self.followings.remove(user)

    def following_tweets(self, tweet_count, offset_count):
        my_followings_tweets = (
            Tweet.query.
            join(user_follow, user_follow.c.following_id == Tweet.tweeted_by).
            filter(user_follow.c.follower_id == self.id).
            order_by(Tweet.tweeted_at.desc()).
            offset(offset_count).
            limit(tweet_count)
        )
        return my_followings_tweets

    def retweets(self):
        return Tweet.query.filter(
            (Tweet.tweeted_by == self.id) &
            (Tweet.is_retweet == True)
        )

class Like(db.Model):
    __tablename__ = 'tweety__like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tweety__user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweety__tweet.id'))


class Tweet(db.Model):
    __tablename__ = 'tweety__tweet'
    id = db.Column(db.Integer, primary_key=True)
    tweeted_by = db.Column(db.Integer, db.ForeignKey('tweety__user.id'))
    text = db.Column(db.String(280))
    tweeted_at = db.Column(db.String(), default=time.time)
    liked_by_me = db.Column(db.Boolean(), default=False)
    likes = db.relationship('Like', backref='tweet', lazy='dynamic', cascade="all,delete")
    #  ^^^^ `cascade`  is for deleting the likes from Like table when a tweet removed
    is_retweet = db.Column(db.Boolean, default=False)
    source_tweet_id = db.Column(db.Integer, db.ForeignKey('tweety__tweet.id'))
    source_tweet = db.relationship(
        'Tweet',
        remote_side=[id],
        backref=db.backref('retweet')
    )

