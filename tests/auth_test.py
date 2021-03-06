from tests.base import BaseTestCase
import unittest
from app.models import User


class AuthTestCate(BaseTestCase):
    def test_user_can_register_correctly(self):
        response = self.client.post('/register',
                                    data={
                                        'username': 'test2',
                                        'email': 'test2@gmail.com',
                                        'password': '123456',
                                        'password_confirm': '123456',
                                        'submit': 'Register'
                                    })
        self.assertRedirects(response, '/')

    def test_login_is_OK(self):
        """ Ensure that login route is up and has no error """
        with self.app.test_client() as c:
            response = c.get('/login')
            self.assertEqual(response.status_code, 200)

    def test_register_is_OK(self):
        """ Ensure that register route is up and has no error"""
        with self.app.test_client() as c:
            response = c.get('/register')
            self.assert200(response)

    def test_insert_user_in_db(self):
        """ Ensure that the models are working fine"""
        user = User.query.get(1)
        self.assertEqual(user.email, 'test@gmail.com')

    def test_index_is_login_required(self):
        """ Ensure that users who are not logged in can not see the index page"""
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=%2F')

    def test_user_logs_in_correctly(self):
        """ Ensure that the user can login successfully with correct credentials """
        response = self.client.post('/login',
                                    data={
                                        'email': 'test@gmail.com',
                                        'password': '123',
                                        'submit': 'Login'
                                    })
        self.assertRedirects(response, '/')

    def test_user_doesnt_log_in_correctly(self):
        """ Ensure that user can not login with wrong credentials"""
        response = self.client.post('/login',
                                    data={
                                        'email': 'wrong@gmail.com',
                                        'password': 'wrong',
                                        'submit': 'Login'
                                    })
        self.assertTemplateUsed('security/login_user.html')


if __name__ == '__main__':
    unittest.main()
