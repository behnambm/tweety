from app import mail, app
import hashlib
from flask import url_for, request

def tweet_text_processor(tweet):
    return tweet['text'].replace('\n', '<br>')


def send_mail(msg):
    mail.send(msg)
    return True


def get_link_hash(user):
    return hashlib.sha256(
                (app.config['SALT_FOR_EMAIL_LINKS'] + str(user.id) + user.email).encode()
            ).hexdigest()


def create_link(hash, email):
    link = url_for('confirm', hash_=hash)
    prefix = request.base_url.split('/')[0:3]
    prefix = '/'.join(prefix)
    args = '?email=' + email
    full_link = prefix + link + args
    print('\n\n\n', full_link)
    return True
