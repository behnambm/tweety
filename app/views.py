from . import app
from flask import render_template, request, jsonify
from .forms import PostTweetForm
from .models import db, Tweet, User, Like
from flask_security import login_required, current_user
import time
from app.schema import TweetSchema
from app.functions import tweet_text_processor


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
            tweeted_at=time.time(),
            tweeted_by=current_user.id
        )
        try:
            db.session.add(tw)
            db.session.commit()
            tweet_schema = TweetSchema()
            tweet = tweet_schema.dump(tw)
            tweet['text'] = tweet_text_processor(tweet)
            tweet['likes'] = len(tweet['likes'])
            return jsonify(tweet), 201
        except Exception as e:  # TODO add logging
            db.session.rollback()
            return 'err', 500


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


@app.route('/profile/get_user_tweet/', methods=['POST'])
@login_required
def get_user_tweet():
    u_id = request.form.get('u_id')
    tweet_count = request.form.get('tweet_count', 10)
    offset_count = request.form.get('offset_count', 0)

    # get tweets from this profile that current_user liked
    liked_tweets = (
        db.session.query(Tweet).
        filter(Tweet.tweeted_by == u_id).
        order_by(Tweet.tweeted_at.desc()).
        offset(offset_count).
        limit(tweet_count).
        from_self().
        join(Like, Like.tweet_id == Tweet.id).
        filter(Like.user_id == current_user.id)
    )

    tweets_from_db = (
        Tweet.query.
        filter_by(tweeted_by=u_id).
        order_by(Tweet.tweeted_at.desc()).
        offset(offset_count).
        limit(tweet_count)
    )

    # mark all the tweets liked by current user
    for tw in liked_tweets.all():
        if tw in tweets_from_db.all():
            tw.liked_by_me = True

    all_tweets = tweets_from_db.union_all(liked_tweets)

    tweet_schema = TweetSchema(many=True)
    tweets = tweet_schema.dump(all_tweets)

    # to put the length of likes in response
    for tweet in tweets:
        tweet['likes'] = len(tweet['likes'])

        # some processes on tweet's text like -> replacing <br> with \n in tweet text
        tweet['text'] = tweet_text_processor(tweet)
    return jsonify(tweets)


@app.context_processor
def post_tweet_form():  # to make post tweet form available in all templates
    return dict(post_tweet_form=PostTweetForm())
