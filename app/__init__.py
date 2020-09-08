from flask import Flask, render_template
from app.models import db, Tweet, User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate
from .forms import ExtendedRegisterForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
import os
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config.from_pyfile('config.cfg')


# database configs
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
# security configs
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']

debug_toolbar = DebugToolbarExtension(app)

db.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)

Security(app, datastore, register_form=ExtendedRegisterForm)


migrate = Migrate(app, db)

if os.environ['FLASK_ENV'] != 'testing':
    # mail configs
    app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
    app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['MAIL_USE_TLS'] = os.environ['MAIL_USE_TLS']
    app.config['SALT_FOR_EMAIL_LINKS'] = os.environ['SALT_FOR_EMAIL_LINKS']
    app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_DEFAULT_SENDER']

mail = Mail(app)

ma = Marshmallow(app)

from app.views import *

