from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_security.forms import RegisterForm
from .models import User


class PostTweetForm(FlaskForm):
    text = TextAreaField(validators=[
            DataRequired(message='Tweet can not be empty.'),
            Length(min=1, max=280, message='Tweet can not be more than 280 characters.')
        ]
    )


class ExtendedRegisterForm(RegisterForm):
    username = StringField(validators=[
            DataRequired(message='Username is required.')
        ]
    )

    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('This username already exists.')
