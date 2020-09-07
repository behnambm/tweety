from . import app
from flask import render_template, request, jsonify, redirect, url_for, flash
from .forms import PostTweetForm, EditProfileForm
from .models import db, Tweet, User, Like, Bookmark
from flask_security import login_required, current_user
import time
from app.schema import TweetSchema, MainTweetSchema
from app.functions import tweet_text_processor, send_mail, get_link_hash, create_link
from email_validator import validate_email
from flask_mail import Message
import os


@app.route('/')
@login_required
def index():
    return render_template('home.html', home_active=True)


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
            text=form.text.data.strip(),
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
            return jsonify(
                message='error while posting tweet'
            ), 500


@app.route('/<username>')
@login_required
def profile(username):
    if username != current_user.username:
        user = User.query.filter_by(username=username).first()
        if user:
            is_this_user_followed_by_current_user = user in current_user.followings.all()
            return render_template(
                'profile.html',
                profile_active=True,
                user=user,
                not_found=False,
                is_this_user_followed_by_current_user=is_this_user_followed_by_current_user)
        else:
            return render_template('profile.html',
                                   profile_active=True,
                                   not_found=True,
                                   username=username)
    else:
        user_to_populate = User.query.get(current_user.id)
        form = EditProfileForm(obj=user_to_populate)
        return render_template('profile.html',
                               profile_active=True,
                               user=current_user,
                               not_found=False,
                               form=form)


@app.route('/profile/get_user_tweet/', methods=['POST'])
@login_required
def get_user_tweet():
    u_id = request.form.get('u_id')
    tweet_count = request.form.get('tweet_count', 10)
    offset_count = request.form.get('offset_count', 0)

    # get tweets from this profile that current_user liked
    liked_tweets = (
        db.session.query(Tweet).
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

    all_tweets = tweets_from_db

    # to mark all the retweets taht liked by current user
    for tweet in all_tweets:
        if tweet.is_retweet:
            if tweet.source_tweet in liked_tweets.all():
                tweet.liked_by_me = True

    tweet_schema = TweetSchema(many=True)
    tweets = tweet_schema.dump(all_tweets)

    # to put the length of likes in response
    for tweet in tweets:
        tweet['likes'] = len(tweet['likes'])

        # calculate lenght of retweet
        if tweet['is_retweet']:
            '''in case of being a retweet'''
            tweet['source_tweet']['retweet'] = len(tweet['source_tweet']['retweet'])
        else :
            '''in case of being a regular tweet'''
            tweet['retweet'] = len(tweet['retweet'])


        # some processes on tweet's text. like -> replacing <br> with \n in tweet text
        tweet['text'] = tweet_text_processor(tweet)
    return jsonify(tweets)


@app.route('/like_tweet/', methods=['POST'])
@login_required
def like_tweet():
    tweet_id = request.form.get('tweet_id')
    try:
        tweet_id = int(tweet_id)
    except Exception as e:  # todo -> add logging
        return jsonify(
            messsage='bad parameter'
        ), 400
    if tweet_id:
        like_row = Like.query.filter_by(user_id=current_user.id, tweet_id=tweet_id).first()
        if not like_row:
            like = Like(tweet_id=tweet_id, user_id=current_user.id)
            try:
                db.session.add(like)
                db.session.commit()
                tweet = Tweet.query.filter_by(id=tweet_id).first()
                likes = tweet.likes.count()
                return jsonify(
                    tweet_id=like.id,
                    action='like',
                    likes=likes
                )
            except Exception as e:  # todo -> add logging
                db.session.rollback()
                return jsonify(
                    message='error while liking'
                ), 500
        else:
            try:
                db.session.delete(like_row)
                db.session.commit()
                tweet = Tweet.query.filter_by(id=tweet_id).first()
                likes = tweet.likes.count()
                return jsonify(
                    tweet_id=like_row.id,
                    action='unlike',
                    likes=likes
                )
            except Exception as e:  # todo -> add logging
                db.session.rollback()
                return jsonify(
                    message='error while unliking'
                ), 500


@app.route('/delete_tweet/', methods=['POST'])
@login_required
def delete_tweet():
    tweet_id = request.form.get('tweet_id')
    if tweet_id:
        tweet = Tweet.query.get(tweet_id)

        # to prevent unauthorized user delete other user's tweets
        if tweet.user != current_user:
            return jsonify(
                message='Unauthorized operation'
            ), 401

        try:
            db.session.delete(tweet)
            db.session.commit()
            return jsonify(
                tweet_id=tweet.id
            ), 200
        except Exception as e:  # todo -> add loggin
            db.session.rollback()
            return jsonify(
                message='error while deleting'
            ), 500
    else:
        return jsonify(
            message='Bad parameter'
        ), 400


@app.route('/follow/', methods=['POST'])
@login_required
def follow():
    user_id_to_follow = request.form.get('username')
    if not user_id_to_follow or user_id_to_follow == current_user.username:
        return jsonify(
            message='bad parameter'
        ), 400

    user = User.query.filter_by(username=user_id_to_follow).first()
    if not user:
        return jsonify(
            message='User does not exist'
        ), 404
    else:
        try:
            current_user.follow(user)
            db.session.commit()
            return jsonify(
                username=user.username
            )
        except Exception as e:  # todo -> add logging
            return jsonify(
                message='error while following'
            ), 500


@app.route('/unfollow/', methods=['POST'])
@login_required
def unfollow():
    username = request.form.get('username')
    if username and username != current_user.username:
        user = User.query.filter_by(username=username).first()
        if user:
            try:
                current_user.unfollow(user)
                db.session.commit()
                return jsonify(
                    username=user.username
                )
            except Exception as e: # todo -> add logging
                db.session.rollback()
                return jsonify(
                    message='error while unfollowing'
                ), 500
        else:
            return jsonify(
                message='user not found'
            ), 404
    else:
        return jsonify(
            message='Bad parameter'
        ), 400


@app.route('/edit_profile/', methods=['POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate():
        try:
            user = User.query.get(current_user.id)
            user.display_name = form.display_name.data
            user.username = form.username.data
            user.bio = form.bio.data
            db.session.commit()
            if user.email != form.email.data and os.environ['FLASK_ENV'] != 'testing':
                # create confirmation link
                link_hash = get_link_hash(user)
                link_to_change_email = create_link(link_hash, form.email.data)
                # create Message to send the mail change confirmation.
                msg = Message(
                    subject='Email change confirmation',
                    recipients=[form.email.data],
                    html=render_template(
                        'email/mail_confirmation.html',
                        sender_name='Tweety',
                        sender_address=app.config['MAIL_DEFAULT_SENDER'],
                        sender_country='Iran',
                        sender_city='Urmia',
                        link=link_to_change_email
                    ),
                    sender=('Tweety', app.config['MAIL_DEFAULT_SENDER'])
                )
                send_mail(msg)
                flash('Please check your email to confirm changes.', 'primary')

        except Exception as e:  # todo -> add logging
            db.session.rollback()
            print(e)
            flash('Something went wrong! Please try again.', 'danger')
    return redirect(url_for('profile', username=current_user.username))


@app.route('/verify_email/', methods=['POST'])
@login_required
def verify_email():
    email = request.form.get('email')
    if email == current_user.email:
        return jsonify(
            message='valid'
        )
    if email:
        try:
            validate_email(email, check_deliverability=False)
            user = User.query.filter_by(email=email).first()
            if user:
                return jsonify(
                    message='Already Taken'
                ), 409
            else:
                return jsonify(
                    message='valid'
                )
        except Exception as e:  # todo -> add logging
            return jsonify(
                message='Bad parameter.'
            ), 400
    else:
        return jsonify(
            message='Bad parameter'
        ), 400


@app.route('/verify_username/', methods=['POST'])
@login_required
def verify_username():
    username = request.form.get('username')
    if username == current_user.username:
        return jsonify(
            message='valid'
        )
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify(
                message='Already Taken'
            ), 409
        else:
            return jsonify(
                message='valid'
            )
    else:
        return jsonify(
            message='Bad parameter'
        ), 400


@app.route('/get_main_tweet/', methods=['POST'])
@login_required
def get_main_tweet():
    tweet_count = request.form.get('tweet_count', 30)
    offset_count = request.form.get('offset_count', 0)

    liked_tweets = (
        db.session.query(Tweet).
        join(Like, Like.tweet_id == Tweet.id).
        filter(Like.user_id == current_user.id)
    )

    tweets_from_db = current_user.following_tweets(tweet_count, offset_count).all()

    # mark tweets that are liked by current_user
    for tweet in tweets_from_db:
        # mark retweets that liked by current user
        if tweet.is_retweet:
            if tweet.source_tweet in liked_tweets:
                tweet.liked_by_me = True

        if tweet in liked_tweets:
            tweet.liked_by_me = True

    # create schema and serialize all tweets coming from DB
    tweet_schema = MainTweetSchema(many=True)
    all_tweets = tweet_schema.dump(tweets_from_db)

    for tweet in all_tweets:
        tweet['likes'] = len(tweet['likes'])

        # calculate lenght of retweet
        if tweet['is_retweet']:
            '''in case of being a retweet'''
            tweet['source_tweet']['retweet'] = len(tweet['source_tweet']['retweet'])
        else:
            '''in case of being a regular tweet'''
            tweet['retweet'] = len(tweet['retweet'])

        # some processes on tweet's text like -> replacing <br> with \n in tweet text
        tweet['text'] = tweet_text_processor(tweet)

    return jsonify(all_tweets)


@app.route('/confirm/<hash_>/')
@login_required
def confirm(hash_=None):
    if hash_:
        email = request.args.get('email')
        if not email:
            return render_template('something_is_not_right.html')

        if current_user.email == email:
            return redirect(url_for('index'))

        hash_from_db = get_link_hash(current_user)
        if hash_ == hash_from_db:
            user = User.query.get(current_user.id)
            user.email = email
            try:
                db.session.commit()
                flash('You have confirmed your email.', 'success')
                return redirect(url_for('profile', username=current_user.username))
            except Exception as e:  # todo -> add logging
                print('\t\t', e)

        return render_template('something_is_not_right.html')
    return redirect(url_for('index'))


@app.route('/bookmarks/')
@login_required
def bookmarks():
    return render_template(
        'bookmarks.html',
        bookmark_active=True
    )


@app.route('/get_bookmarks/', methods=['POST'])
@login_required
def get_bookmarks():
    try:
        liked_tweets = (
            db.session.query(Tweet).
            join(Like, Like.tweet_id == Tweet.id).
            filter(Like.user_id == current_user.id)
        ).all()

        offset_count = request.form.get('offset_count', 0)
        tweet_count = request.form.get('tweet_count', 20)
        tweets = (
            db.session.query(Tweet).
            join(Bookmark, Bookmark.tweet_id == Tweet.id).
            filter(User.id == Bookmark.user_id).
            order_by(Bookmark.created_at.desc()).
            offset(offset_count).
            limit(tweet_count)
        ).all()

        # mark liked tweet by current user
        for tweet in tweets:
            if tweet in liked_tweets:
                tweet.liked_by_me = True

        schema = MainTweetSchema(many=True)
        all_tweets = schema.dump(tweets)
        prefix = request.base_url.split('/')[0:3]

        for tweet in all_tweets:
            # generate appropriate path for avatar if it's a retweet
            if tweet['is_retweet']:
                tweet['source_tweet']['user']['avatar_path'] = (
                                       '/'.join(prefix) +
                                       '/' +
                                       tweet['source_tweet']['user']['avatar_path']
                )

            # calculate lenght of retweet
            if tweet['is_retweet']:
                '''in case of being a retweet'''
                tweet['source_tweet']['retweet'] = len(tweet['source_tweet']['retweet'])
            else:
                '''in case of being a regular tweet'''
                tweet['retweet'] = len(tweet['retweet'])
                
            tweet['user']['avatar_path'] = '/'.join(prefix) + '/' + tweet['user']['avatar_path']
            tweet['likes'] = len(tweet['likes'])
            # some processes on tweet's text like -> replacing <br> with \n in tweet text
            tweet['text'] = tweet_text_processor(tweet)

        return jsonify(all_tweets)
    except Exception as e:  # todo -> add logging
        print('\n\n\n', e)
        pass
        return jsonify(
            message='something went wrong'
        ), 500


@app.route('/add_to_bookmarks/', methods=['POST'])
@login_required
def add_to_bookmarks():
    tweet_id = request.form.get('tweet_id')
    if tweet_id:
        tweet = Tweet.query.get(tweet_id)
        # prevent adding tweets that belongs to current user
        if tweet.tweeted_by == current_user.id:
            return jsonify(
                message='you cant bookmark your tweets'
            ), 400
        if tweet:
            tweet_in_bookmark = Bookmark.query.filter_by(tweet_id=tweet_id).first()
            if tweet_in_bookmark:
                return jsonify(
                    message='already in bookmark'
                ), 409
            try:
                tweet_to_bookmark = Bookmark(user_id=current_user.id, tweet_id=tweet_id)
                db.session.add(tweet_to_bookmark)
                db.session.commit()
                return jsonify(
                    message='add to bookmarks'
                ), 200
            except Exception as e:
                pass
                return jsonify(
                    message='error in server side'
                ), 500
    return jsonify(
        message='bad parameter'
    ), 400


@app.route('/delete_bookmark/', methods=['POST'])
@login_required
def delete_bookmark():
    tweet_id = request.form.get('tweet_id')
    if tweet_id:
        try:
            tweet = Bookmark.query.\
                filter_by(user_id=current_user.id).\
                filter_by(tweet_id=tweet_id).first()
            db.session.delete(tweet)
            db.session.commit()
            return jsonify(
                message='tweet deleted'
            ), 200
        except Exception as e:
            print('\n\n\n\tXXX', e)
            db.session.rollback()
            return jsonify(
                messsage='something went wrong'
            ), 500
    return jsonify(
        message='bad parameter'
    ), 400


@app.context_processor
def post_tweet_form():  # to make post tweet form available in all templates
    return dict(post_tweet_form=PostTweetForm())
