$(document).ready(function () {

    function update_timeline(tweet_count, offset_count) {
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/profile/get_user_tweet/',
            type: 'POST',
            data: {
                'u_id': u_id,
                'tweet_count': tweet_count ? tweet_count : 100,
                'offset_count': offset_count ? offset_count : 0
            },
            statusCode: {
                200: function (response) {
                    if (response.length > 0) {
                        response.forEach(function (tweet) {

                            $('.tweets-list').append(generate_tweet(tweet));
                        })
                    } else {
                        $('.tweets-list').append('<h4 class="no-tweets-yet tc"><br>No tweets yet</h4>')
                    }
                }
            }
        });
    }
    update_timeline();
});