from app import ma
from app.models import Tweet, User
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class TweetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
        fields = ('id', 'likes', 'text', 'tweeted_at', 'tweeted_by', 'liked_by_me')
        include_fk = True
        include_relationships = True


class MainUserSchema(ModelSchema):
    class Meta:
        model = User
        fields = (
            'avatar_path',
            'username',
            'display_name',
            'id '
        )


class MainTweetSchema(ModelSchema):
    class Meta:
        model = Tweet
        include_fk = True
        include_relationships = True
        exclude = (
            'tweeted_by',
        )
    user = fields.Nested(MainUserSchema)
