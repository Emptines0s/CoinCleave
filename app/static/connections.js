$(document).ready(function() {
  function update_connection_status(ping_url, connection_id) {
    $.ajax({
        type: 'GET',
        url: ping_url,
        success: function(request) {
            if (request.state != 'PENDING') {
                $('#' + connection_id).find('.conn-ping-state').text(request.result)
            }
            else {
                setTimeout(update_connection_status, 1000, ping_url, connection_id);
            }
        }
    });
  };

  $('.ping-button').click(function() {
    $.ajax({
      type: 'POST',
      url: '/connection_ping',
      data: {'connection_id': $(this).parent().parent().attr('id')},
      success: function(request) {
          $('#' + request.connection_id).find('.conn-ping-state').text('Ping connection...')
          update_connection_status(request.Location, request.connection_id);
      },
      error: function() {
          alert('Unexpected error');
      }
    });
  });

  $('.delete-button').click(function() {
    $.ajax({
      type: 'POST',
      url: '/delete_connection',
      data: {'connection_id': $(this).parent().parent().attr('id')},
      success: function(request) {
        $("#" + request.connection_id).remove();
      }
    });
  });
});