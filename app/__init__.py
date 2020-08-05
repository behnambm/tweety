from flask import Flask, render_template
from app.models import db, Tweet, User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from flask_migrate import Migrate
from .forms import ExtendedRegisterForm
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

debug_toolbar = DebugToolbarExtension(app)

db.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)

Security(app, datastore, register_form=ExtendedRegisterForm)


migrate = Migrate(app, db)

from app.views import *


@app.before_first_request
def db_stuff():
    from app.models import db
    db.create_all()
    print('s')