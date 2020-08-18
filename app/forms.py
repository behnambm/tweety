from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField
from wtforms.validators import DataRequired, Length, ValidationError, Email
from flask_security.forms import RegisterForm
from app.models import User
from flask_security import current_user


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


class EditProfileForm(FlaskForm):
    display_name = StringField()
    username = StringField()
    bio = TextAreaField()
    email = StringField(validators=[Email()])

    def validate_email(form, field):
        if field.data != current_user.email:
            user = User.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError('Email Already Taken.')

    def validate_username(form, field):
        if field.data != current_user.username:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError('Username Already Taken')

