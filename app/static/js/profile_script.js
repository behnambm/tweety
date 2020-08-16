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


    // like and unlike tweets
    $(document).on('click', '.like-tweet',function (e) {
        let svg_elem_id_array = $(this).attr('id').split('-');
        let tweet_id = svg_elem_id_array.pop();
        if (tweet_id == 'fill'){
            tweet_id = svg_elem_id_array.pop();
        }
        if (tweet_id) {
            $.ajax({
                url: document.location.protocol + '//' + document.location.host + '/like_tweet/',
                type: 'POST',
                data: {
                    tweet_id: tweet_id
                },
                statusCode: {
                    200: function (response) {
                        if ( response['action'] == 'like'){
                            $('#heart-svg-' + tweet_id).hide();
                            $('#heart-svg-' + tweet_id + '-fill').show();
                            let like_count = (response['likes'] > 0) ? response['likes'] : '';
                            $('#like-count-' + tweet_id).text(like_count);
                        } else if ( response['action'] == 'unlike'){
                            $('#heart-svg-' + tweet_id + '-fill').hide();
                            $('#heart-svg-' + tweet_id).show();

                        } else{
                            // todo -> show some message to the user to get noticed that something is wrong
                        }
                        let like_count = (response['likes'] > 0) ? response['likes'] : '';
                        $('#like-count-' + tweet_id).text(like_count);
                    }
                }
            });
        }
    });

    // set tweet id to confirm the deletion
    $(document).on('click', '.delete-tweet', function () {
        let tweet_id = $(this).attr('id').split('-').pop();
        $('#tweet-id-to-delete').text(tweet_id);
    });


    // send ajax to delte the tweet
    $('#delete-tweet-btn').click(function () {
        let tweet_id = $('#tweet-id-to-delete').text();

        if (tweet_id !== null){
            $.ajax({
                url: document.location.protocol + '//' + document.location.host + '/delete_tweet/',
                type: 'POST',
                data:{
                    tweet_id: tweet_id
                },
                statusCode: {
                    200: function (response) {
                        $('.tweet[data-id='+ tweet_id +']').remove();
                        $('#confirm-delete-modal').modal('hide');
                        $('#exampleFormControlTextarea1').val('');
                        generate_alert('You have deleted a tweet!', 3500, 'delete-alert');
                    }
                }
            })
        }
    });

});