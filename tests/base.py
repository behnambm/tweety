import unittest
from flask_testing import TestCase
from app import app
import os
from app.models import db
from app import datastore
from flask_security.utils import hash_password
from datetime import datetime


class BaseTestCase(TestCase):
    """ A base test case for testing the twitter app"""

    def create_app(self):
        """ This method will be executed for each unit test"""

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
            os.path.dirname(os.path.abspath(__name__)),
            'test_db.sqlite'
        )
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        with app.app_context():
            db.create_all()
            s = datastore.create_user(
                username='test',
                email='test@gmail.com',
                password=hash_password('123'),
                active=True,
                confirmed_at=datetime.utcnow(),
                last_login_at=datetime.utcnow(),
                current_login_at=datetime.utcnow(),
                last_login_ip='127.0.0.1',
                current_login_ip='127.0.0.1',
                avatar_path='/tmp/avatar.png',
                bio='Just a tech :|',
                display_name='Behnumm :)'
            )
            db.session.add(s)
            db.session.commit()
        return app

    def tearDown(self):
        """ Clean database after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    @classmethod
    def tearDownClass(cls):
        """ TO clean everything from filesystem when all tests are done """
        # get the dirname to here `tests`
        dirname_to_here = os.path.dirname(os.path.abspath(__name__))
        # join `tests` and database name `test_db.sqlite`
        full_path_to_db = os.path.join(dirname_to_here, 'test_db.sqlite')
        # delete the testing database
        os.unlink(full_path_to_db)



