$(document).ready(()=>{

    function sleep (time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }

    // auto focus the `text area` when user wants to write a tweet
    $('.modal').on('shown.bs.modal', function () {
      $('#exampleFormControlTextarea1').trigger('focus');
    });

    // to handle 280 characters inside the textarea 
    $('#exampleFormControlTextarea1').keyup(e =>{
        let tweetText = $(e.target).val();
        if (tweetText.length > 280){
            $(e.target).val(tweetText.slice(0, 280));
            $(e.target).css('box-shadow', '0 0 5px 0 red');
        } else {
            $(e.target).css('box-shadow', 'dodgerblue 0px 0px 5px 0px');
        }
    });

    // use ajax to post tweet
    $('#post-tweet-btn-modal').click( e =>{
        e.preventDefault();
        let tweetText = $('#exampleFormControlTextarea1').val();
        let csrf_token = $('#csrf_token').val();
        $('.modal').modal('hide');
        $.ajax({
            url: document.location.protocol + '//' + document.location.host + '/post_tweet/',
            type: 'POST',
            data: {
                'text': tweetText,
                'csrf_token': csrf_token
            },
            statusCode:{
                201: function (response) {
                    $('#message-alert-text').text('you have posted a tweet');
                    $('#message-alert-custom').fadeIn('slow');
                    sleep(3500).then(()=>{
                        $('#message-alert-custom').fadeOut('slow');
                        $('#exampleFormControlTextarea1').val('');
                    });

                    // (first condition)                    to update timeline after posting a tweet
                    // (second condition explanation )      i use below code to avoid appending
                    //                                      tweet to the timeline that is not belong
                    //                                      to the current user.
                    if (document.location.pathname != '/' && current_user == username) {
                        $('.no-tweets-yet').remove();
                        $('.tweets-list').prepend(generate_tweet(response))
                    }
                },
                500: function () {
                    console.log('there is an error.');
                }
            }
        });
    });
});

// tweet generator function
function generate_tweet(tweet_data){
        let final_time = moment(tweet_data['tweeted_at'] * 1000).fromNow(true);
        let time_to_show_to_user = '';
        let sliced_time = final_time.split(' ')
        if (final_time == 'a minute'){
            time_to_show_to_user = '1m';
        } else if (sliced_time[1] == 'minutes'){
            time_to_show_to_user = sliced_time[0] + 'm';
        } else if (final_time == 'an hour'){
            time_to_show_to_user = '1h';
        } else if (sliced_time[1] == 'hours'){
            time_to_show_to_user = sliced_time[0] + 'h';
        } else if (final_time == 'a day'){
            time_to_show_to_user = '1d';
        } else if (sliced_time[1] == 'days' || sliced_time[1].indexOf('year') != -1 ){
            if ((sliced_time[1] == 'days' && parseInt(sliced_time[0]) > 6) || final_time.indexOf('year') != -1){
                let date_obj = new Date(tweet_data['tweeted_at'] * 1000);
                let month = date_obj.toLocaleString('default', {month: 'long'});
                let day = date_obj.getDate();
                time_to_show_to_user = month + ' ' + day;
            } else {
                time_to_show_to_user = sliced_time[0] + 'd'
            }
        } else {
            console.log('something is wrong if you can see this' + sliced_time);
        }
        let is_liked = false;
        if (tweet_data['liked_by_me'] == true){
            is_liked = true;
        }

        let tweet_div = `
        <div class="tweet">
            <div class="tweet-head">
                <div class="tweet-user-link-area">
                <div class="user-avatar fl">
                    <img src="${avatar_path}" alt="this user">
                </div>
                <div class="user-name fl">
                    ${display_name}
                </div>
                <div class="user-username fl">
                    @${username}
                </div>
                </div>
                <div class="dot" style="float: left;">.</div>
                <div class="tweet-datetime fl">${time_to_show_to_user}</div>
            </div>
            <div class="clear"></div>
            <div class="tweet-body">
                <div class="tweet-text">
                    ${tweet_data['text']}
                </div>
                <div class="tweet-media"></div>
            </div>
            <div class="tweet-footer">
                <div class="row">
                    <div class="tweet-footer-reply col-2">
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-chat cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z"/>
                        </svg>
                    </div>
                    <div class="tweet-footer-retweet col-3">
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-arrow-repeat cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M2.854 7.146a.5.5 0 0 0-.708 0l-2 2a.5.5 0 1 0 .708.708L2.5 8.207l1.646 1.647a.5.5 0 0 0 .708-.708l-2-2zm13-1a.5.5 0 0 0-.708 0L13.5 7.793l-1.646-1.647a.5.5 0 0 0-.708.708l2 2a.5.5 0 0 0 .708 0l2-2a.5.5 0 0 0 0-.708z"/>
                            <path fill-rule="evenodd" d="M8 3a4.995 4.995 0 0 0-4.192 2.273.5.5 0 0 1-.837-.546A6 6 0 0 1 14 8a.5.5 0 0 1-1.001 0 5 5 0 0 0-5-5zM2.5 7.5A.5.5 0 0 1 3 8a5 5 0 0 0 9.192 2.727.5.5 0 1 1 .837.546A6 6 0 0 1 2 8a.5.5 0 0 1 .501-.5z"/>
                        </svg>
                    </div>
                    <div class="tweet-footer-like col-3">
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-heart ${is_liked ? 'hide' : ''} cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M8 2.748l-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/>
                        </svg>
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-heart-fill ${is_liked ? 'show-heart' : '' } cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
                        </svg>
                        <span class="likes-count">${tweet_data['likes'] > 0 ? tweet_data['likes'] : ''}</span>
                    </div>
                    <div class="tweet-footer-bookmark col-1">
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-bookmark cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M8 12l5 3V3a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12l5-3zm-4 1.234l4-2.4 4 2.4V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10.234z"/>
                        </svg>
                    </div>
                    <div class="tweet-footer-share col-1">
                        <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-share cp" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M11.724 3.947l-7 3.5-.448-.894 7-3.5.448.894zm-.448 9l-7-3.5.448-.894 7 3.5-.448.894z"/>
                            <path fill-rule="evenodd" d="M13.5 4a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm0 1a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm0 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm0 1a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm-11-6.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm0 1a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
                        </svg>
                    </div>
                </div>
            </div>
            <hr>
        </div>
        `;
        return tweet_div;
    }
