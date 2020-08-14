from app import ma
from app.models import Tweet
from marshmallow import fields


class TweetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
        fields = ('id', 'likes', 'text', 'tweeted_at', 'tweeted_by', 'liked_by_me')
        include_fk = True
        include_relationships = True

