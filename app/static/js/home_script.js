$(document).ready(function () {

function updateMainTimeline(tweet_count, offset_count) {
    $.ajax({
        url: document.location.protocol + '//' + document.location.host + '/get_main_tweet/',
        type: 'POST',
        data: {
            'tweet_count': tweet_count ? tweet_count : 30,
            'offset_count': offset_count ? offset_count : 0
        },
        statusCode: {
            200: function (response) {
                if (response.length > 0) {
                    response.forEach(function (tweet) {
                        $('.time-line').append(generate_tweet(tweet, 'main'));
                    });

                } else {
                    $('.time-line').append('<h4 class="no-tweets-yet tc"><br>No tweets yet</h4>')
                }
            }
        }
    });
}
updateMainTimeline();

});