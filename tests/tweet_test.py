from tests.base import BaseTestCase
import unittest


class TweetTestCase(BaseTestCase):
    """ Unit tests for tweet related stuff"""

    def test_post_tweet_works(self):
        with self.app.test_client() as c:
            c.post('/login',
                   data={
                       'email': 'test@gmail.com',
                       'password': '123',
                       'submit': 'Login'
                   })
            response = c.post("/post_tweet/",
                              data={
                                  'text': 'testing tweet'
                              })
            self.assertStatus(response, 201)


if __name__ == '__main__':
    unittest.main()
