from . import app
from flask import render_template, abort
from .forms import PostTweetForm
from .models import db, Tweet, User
from flask_security import login_required, current_user
from datetime import datetime


@app.route('/')
@login_required
def index():
    return render_template('home.html')


@app.route('/<username>/<int:tweet_id>')
@login_required
def single_tweet(username, tweet_id):
    return render_template('single_tweet.html')


@app.route('/post_tweet/', methods=['POST'])
@login_required
def post_tweet():
    form = PostTweetForm()
    if form.validate():
        tw = Tweet(
            text=form.text.data,
            tweeted_at=datetime.utcnow(),
            tweeted_by=current_user.id
        )
        try:
            db.session.add(tw)
            db.session.commit()
        except Exception as e:  # TODO add logging
            db.session.rollback()
            return 'err', 500
    return 'ok', 201


@app.route('/<username>')
@login_required
def profile(username):
    if username != current_user.username:
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('profile.html',
                                   profile_active=True,
                                   user=user,
                                   not_found=False)
        else:
            return render_template('profile.html',
                                   profile_active=True,
                                   not_found=True,
                                   username=username)

    return render_template('profile.html',
                           profile_active=True,
                           user=current_user,
                           not_found=False)


@app.context_processor
def post_tweet_form():  # to make post tweet form available in all templates
    return dict(post_tweet_form=PostTweetForm())
