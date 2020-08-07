$(document).ready(()=>{

    function sleep (time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }

    // auto focus the `text area` when user wants to write a tweet
    $('.modal').on('shown.bs.modal', function () {
      $('#exampleFormControlTextarea1').trigger('focus');
    })

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
                201: function () {
                    $('#message-alert-text').text('you have posted a tweet');
                    $('#message-alert-custom').fadeIn('slow');
                    sleep(3500).then(()=>{
                        $('#message-alert-custom').fadeOut('slow');
                        $('#exampleFormControlTextarea1').val('');
                    });
                },
                500: function () {
                    console.log('there is an error.');
                }
            }
        });
    });
});