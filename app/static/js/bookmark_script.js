$(document).ready(function () {
    function get_bookmarks(tweet_offset, tweet_count){
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/get_bookmarks/',
            type: 'POST',
            data: {
                user_id: current_user_id,
                offset_count: tweet_offset ? tweet_offset : 0,
                tweet_count: tweet_count ? tweet_count : 20
            },
            statusCode: {
                200: function (response) {
                    if (response.length == 0){
                        $('.time-line').append('<h4 class="no-tweets-yet tc"><br>No bookmarks.</h4>');
                    } else {
                        response.forEach(function (tweet) {
                            $('.time-line').append(generate_tweet(tweet, 'main'));
                        })
                    }
                }
            }
        });
    }

    get_bookmarks();
});