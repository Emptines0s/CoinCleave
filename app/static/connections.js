$(document).ready(function() {
  function update_connection_status(ping_url, connection_id) {
    $.ajax({
        type: 'GET',
        url: ping_url,
        success: function(request) {
            if (request.state != 'PENDING') {
                document.getElementById(connection_id).innerHTML = request.result;
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
      data: {'connection_id': $(this).parent().attr('id')},
      success: function(request) {
          $("#" + request.connection_id).text(request.Location);
          update_connection_status(request.Location, request.connection_id);
      },
      error: function() {
          alert('Unexpected error');
      }
    });
  });

  $('.delete-button').click(function() {
    alert('123123');
    $.ajax({
      type: 'POST',
      url: '/delete_connection',
      data: {'connection_id': $(this).parent().attr('id')},
      success: function(request) {
        $("#" + request.connection_id).remove();
      }
    });
  });
});