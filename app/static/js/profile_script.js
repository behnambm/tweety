$(document).ready(function () {

    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })

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


    // follow users
    $('#follow-user-btn').click(function () {
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/follow/',
            type: 'POST',
            data: {
                username: username
            },
            statusCode: {
                200: function (response) {
                    if (response['username'] == username) {
                        $('#follow-user-btn').attr('id', 'unfollow-user-btn');
                        $('#unfollow-user-btn').text('Unfollow');
                    }
                }
            }
        });
    });


    // unfollow users
    $(document).on('click', '#unfollow-user-btn', function () {
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/unfollow/',
            type: 'POST',
            data: {
                username: username
            },
            statusCode: {
                200: function (response) {
                    if (response['username'] == username){
                        $('#unfollow-user-btn').attr('id', 'follow-user-btn');
                        $('#follow-user-btn').text('Follow');
                    }
                }
            }
        });
    });


    // calculate length of input in edit profile section
    $('.bio-input').focus(function () {
        $(this).keyup(function (e) {
            let input_len = $(this).val().length;
            let target_element = $('#input-length-' + $(this).attr('id'));
            let max_length = target_element.data('length');
            if (input_len <= max_length) {
                target_element.text(input_len + ' / ' + max_length);
            } else {
                let sliced_text = $(this).val().slice(0, max_length);
                $(this).val(sliced_text);
            }
        });
    });


    // trim the input text
    function trimInput(_this) {
        $(_this).val( $(_this).val().trim());
        let input_len = $(_this).val().length;
        let target_element = $('#input-length-' + $(_this).attr('id'));
        let max_length = target_element.data('length');
        target_element.text(input_len + ' / ' + max_length);
    }


    // validate integration of fields
    function validateField(field) {
        let fieldName = $(field).attr('name');
        let data = null;
        if (fieldName == 'username'){
            data = {
                username: $(field).val()
            }
        } else if (fieldName == 'email'){
            data = {
                email: $(field).val()
            }
        }
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/verify_' + fieldName + '/',
            type: 'POST',
            data: data,
            statusCode:{
                200: function (response) {
                    if (response['message'] == 'valid') {
                        $('#invalid-' + fieldName).hide();
                        $('#valid-' + fieldName).css('display', 'flex');
                    }
                },
                400: function (response) {
                    $('#valid-' + fieldName).hide();
                    $('#invalid-' + fieldName).css('display', 'flex');
                },
                409: function (response) {
                    $('#valid-' + fieldName).hide();
                    $('#invalid-' + fieldName).css('display', 'flex');
                }
            }
        });
    }

    // to check the availability of username and email
    $('.bio-input').focusout(function () {
        trimInput(this);
        let fieldName = $(this).attr('name');
        if (fieldName == 'email' || fieldName == 'username'){
            validateField(this);
        }
    });

});