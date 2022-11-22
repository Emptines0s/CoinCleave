$(document).ready(function() {
  $(document).click(function(e){
    if($(e.target).closest('.popup_activity_list').length == 0 && $('.popup_activity_list').hasClass("active")) {
      $('.popup_black_back').fadeOut();
      $('.popup_activity_list').fadeOut();
      $('.popup_activity_list').removeClass("active");
    }
  });

  $('.purchase_history').click(function() {
    $('.popup_black_back').fadeIn();
    $('.popup_activity_list').fadeIn(function() {
      $('.popup_activity_list').addClass("active");
    });
  });

  $('._30d-gradient').click(function() {
    $.ajax({
        type: 'POST',
        url: '/buy_subscription',
        data: {'subscription_name': '30 days', 'subscription_time': 1},
        success: function() {
            alert('Unexpected error');
        }
    });
  });
});