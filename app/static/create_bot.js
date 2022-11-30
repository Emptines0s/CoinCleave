$(document).ready(function() {
  $( ".create-bot-connect" )
  .change(function () {
    var str = "";
    $( ".create-bot-connect option:selected" ).each(function() {
      str += $( this ).text();
    });
    $.ajax({
      type: 'POST',
      url: '/get_connect_info',
      data: {'connect_api': str},
      success: function(request) {
        $('.connect-description').text("Подключённая биржа: " + request.info);
      }
    });
  })
  .change();

  $( ".create-bot-strategy" )
  .change(function () {
    var str = "";
    $( ".create-bot-strategy option:selected" ).each(function() {
      str += $( this ).text();
    });
    $.ajax({
      type: 'POST',
      url: '/get_strategy_info',
      data: {'strategy_name': str},
      success: function(request) {
        $('.strategy-description').text(request.info);
      }
    });
  })
  .change();
});