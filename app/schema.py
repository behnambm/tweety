from app import ma
from app.models import Tweet, User
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class MainUserSchema(ModelSchema):
    class Meta:
        model = User
        fields = (
            'avatar_path',
            'username',
            'display_name',
            'id',
            'bio'
        )


class TweetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
        include_fk = True
        include_relationships = True
    source_tweet = fields.Nested('self', default=None)
    user = fields.Nested(MainUserSchema)


class MainTweetSchema(ModelSchema):
    class Meta:
        model = Tweet
        include_fk = True
        include_relationships = True
        exclude = (
            'tweeted_by',
        )
    user = fields.Nested(MainUserSchema)
    source_tweet = fields.Nested('self', default=None)