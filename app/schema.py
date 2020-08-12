from app import ma
from app.models import Tweet


class TweetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tweet
        fields = ('id', 'likes', 'text', 'tweeted_at', 'tweeted_by')
        include_fk = True
        include_relationships = True

