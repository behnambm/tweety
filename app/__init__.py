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

debug_toolbar = DebugToolbarExtension(app)

db.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)

Security(app, datastore, register_form=ExtendedRegisterForm)


migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = os.environ['MAIL_USE_TLS']
mail = Mail(app)

ma = Marshmallow(app)

from app.views import *

