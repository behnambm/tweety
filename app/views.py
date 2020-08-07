from . import app
from flask import render_template, redirect, url_for
from .forms import PostTweetForm
from .models import db, Tweet
from flask_security import login_required, current_user
from datetime import datetime


@app.route('/')
@login_required
def index():
    return render_template('home.html')


@app.route('/behnumm/<int:tweet_id>')
@login_required
def single_tweet(tweet_id):
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



@app.context_processor
def post_tweet_form():  # to make post tweet form available in all templatas
    return dict(post_tweet_form=PostTweetForm())
