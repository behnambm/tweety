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
                            $('.time-line').append(generate_tweet(tweet, 'bookmark'));
                            $(function () {
                              $('[data-toggle="tooltip"]').tooltip()
                            })
                        })
                    }
                }
            }
        });
    }

    get_bookmarks();

    // delete tweets from bookmarks
    $(document).on('click', '.delete-bookmarked-tweet', function () {
        let parent_elem = $(this).parents('.tweet');
        let tweet_id = parent_elem.data('id');
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/delete_bookmark/',
            type: 'POST',
            data: {
                tweet_id: tweet_id
            },
            statusCode: {
                200: function (response) {
                    $('[data-toggle="tooltip"]').tooltip('dispose');
                    parent_elem.remove();
                    generate_alert('Tweet removed from your bookmarks', 3500, 'tweet-post-alert')
                    $('[data-toggle="tooltip"]').tooltip();
                }
            }
        });
    });



});