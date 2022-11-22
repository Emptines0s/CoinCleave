$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  let room = "BTCUSDT";
  joinRoom("BTCUSDT");

  socket.on('trade', function(msg) {
      $("#testid").text(msg)
      console.log('Received message');
  });

  $(".line").click(function(){
    if (this.id != room) {
        alert(this.id);
        leaveRoom(room);
        joinRoom(this.id);
        room = this.id;
//        trade_chart.data.datasets[0].data = [7, 7, 7, 7, 7, 7, 9];
//        trade_chart.update();
    }
  });

  function leaveRoom(room) {
    socket.emit('leave', {'room': room});
  };

  function joinRoom(room) {
    socket.emit('join', {'room': room});
  };

  $(".start_bot").click(function() {
    alert('31231321233123');
    $.ajax({
    type: 'POST',
    url: '/start_bot',
    data: {'bot_id': room},
    success: function() {
      }
    });
  });

  $(".soft_stop").click(function() {
    alert('31231321233123');
    $.ajax({
    type: 'POST',
    url: '/soft_stop_bot',
    data: {'bot_id': room},
    success: function() {
      }
    });
  });

  $(".hard_stop").click(function() {
    alert('31231321233123');
    $.ajax({
    type: 'POST',
    url: '/hard_stop_bot',
    data: {'bot_id': room},
    success: function() {
      }
    });
  });

  const labels = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
  ];

  const data = {
    labels: labels,
    datasets: [{
      label: 'TRADING PAIR',
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      data: [0, 10, 5, 2, 20, 30, 45],
    }]
  };

  const config = {
    type: 'line',
    data: data,
    options: {
      plugins: {
        legend: {
            display: false
        }
      }
    }
  };

  const trade_chart = new Chart(
    document.getElementById('trade_chart'),
    config
  );
});