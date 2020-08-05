$(document).ready(()=>{
    
    // to handle 280 characters inside the textarea 
    $('#exampleFormControlTextarea1').keyup(e =>{
        let tweetText = $(e.target).val();

        if (tweetText.length > 280){
            $(e.target).val(tweetText.slice(0, 280));
            $(e.target).css('box-shadow', '0 0 5px 0 red');
        } else {
            $(e.target).css('box-shadow', 'none');

        }

    });
});