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
                'tweet_count': tweet_count ? tweet_count : 20,
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


    // get list of followings
    $('#followingsModal').on('shown.bs.modal', function (e) {
      let count_of_followings = $('#followings-count-input').val();
      let count_of_skip_followings = $('#followings-skip-count-input').val();
      $.ajax({
          url: generateUrl(username + '/followings/'),
          type: 'POST',
          data: {
              count: count_of_followings,
              skip_count: count_of_skip_followings
          },
          beforeSend: function () {
            // show loading gif
          },
          statusCode: {
              200: function (response) {
                if (typeof response == 'object') {
                    response_object = Object.values(response);
                    if (response_object.length > 0){
                        users = response_object[0];
                        if (users.length > 0){
                          users_list = generateShortProfile(users);
                          $('#followingsModal .modal-body').append(users_list);
                        } else {
                           $('#followingsModal .modal-body').text('No followings.');
                        }
                    }
                }
                // hide loading gif
              },
              400: function (response) {
                  console.log('something is went wrong')
              }
          }
      });
    });


    // get list of followers
    $('#followersModal').on('shown.bs.modal', function (e) {
      let count_of_followers = $('#followers-count-input').val();
      let count_of_skip_followers = $('#followers-skip-count-input').val();
      $.ajax({
          url: generateUrl(username + '/followers/'),
          type: 'POST',
          data: {
              count: count_of_followers,
              skip_count: count_of_skip_followers
          },
          beforeSend: function () {
            // show loading gif
          },
          statusCode: {
              200: function (response) {
                if (typeof response == 'object') {
                    response_object = Object.values(response);
                    if (response_object.length > 0){
                        users = response_object[0];
                        if (users.length > 0){
                          users_list = generateShortProfile(users);
                          $('#followersModal .modal-body').append(users_list);
                        } else {
                           $('#followersModal .modal-body').text('No followers.');
                        }
                    }
                }
                // hide loading gif
              },
              400: function (response) {
                  console.log('something is went wrong')
              }
          }
      });
    });


    // to clear users list after closing followings modal
    $('#followingsModal').on('hidden.bs.modal', function (e) {
        $('#followingsModal .modal-body').empty();
    });


    // to clear users list after closing followers modal
    $('#followersModal').on('hidden.bs.modal', function (e) {
        $('#followersModal .modal-body').empty();
    });


});


function generateShortProfile(userProfile) {
    let all_rows = ``;
    userProfile.forEach(function (user) {

        let avatar_link = generateUrl(user['avatar_path']);
        let link_to_profile = generateUrl(user['username']);
        let trailing_3dot = ( user['bio'] != null && user['bio'].length > 27) ? '...' : ''
        let current_row =` 
        <div class="row">
            <a href="${link_to_profile}">
                <div class="col-2">
                    <a href="${link_to_profile}">
                        <img src="${avatar_link}" class="users-list-user-avatar">
                </div>
                <div class="col-6">
                    <div class="user-info-holder">
                        <span class="user-display-name">${user['display_name'] ? user['display_name'] : user['username']}</span> .
                        <span class="user-username">${user['username']}</span>
                    </a>
                    </div>
                    <div class="user-bio-holder">
                        <span class="user-bio">${user['bio'] ? user['bio'].substring(0, 30, '...') : ''} ${trailing_3dot}</span>
                    </div>
                </div>
            </a>
            ${ user['username'] != current_user_username ?
                user['followed_by_me'] ?
                    `<div class="col-4 button-holder">
                        <button class="unfollow-btn" onclick="followUser('${user['username']}', this)" data-userid="${user['id']}">Unfollow</button>
                    </div>`
                    : 
                    `<div class="col-4 button-holder">
                        <button class="follow-btn" onclick="followUser('${user['username']}', this)" data-userid="${user['id']}">Follow</button>
                    </div>`
            : ''}
        </div>
        `;
        all_rows += current_row;
    });

    let users_list = `
        <div class="users-list">
        ${all_rows}
        </div>
    `;
    return users_list
}

function followUser(username, this_elem) {
    let current_text = $(this_elem).text();
    if (current_text == 'Follow'){
        // ajax request to unfollow user
        $.ajax({
            url: generateUrl('follow/'),
            type: 'POST',
            data: {
                username: username
            },
            statusCode: {
                200: function (response) {
                    $(this_elem).removeClass('follow-btn');
                    $(this_elem).addClass('unfollow-btn');
                    $(this_elem).text('Unfollow')
                }
            }
        })
    } else {
        // ajax request to unfollow user
        $.ajax({
            url: generateUrl('unfollow/'),
            type: 'POST',
            data: {
                username: username
            },
            statusCode: {
                200: function (response) {
                    $(this_elem).removeClass('unfollow-btn');
                    $(this_elem).addClass('follow-btn');
                    $(this_elem).text('Follow')
                }
            }
        })
    }
}