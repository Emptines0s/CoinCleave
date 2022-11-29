$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  let room = 'None';

  socket.on('trade', function(msg) {
    $('.trade-history-list').empty();
    for (let i = 0; i < msg.trades_data.length; i++) {
      var $newTrade = $('<div/>').addClass('trade-line');
      if (i == msg.trades_data.length - 1) {
        $newTrade.css("border-bottom", "0");
      }
      $newTrade.append('<div class="trade-unit">' + msg.trades_data[i][0] + '<div>');
      $newTrade.append('<div class="trade-unit">' + msg.trades_data[i][1] + '<div>');
      $newTrade.append('<div class="trade-unit">' + msg.trades_data[i][2] + '<div>');
      $newTrade.append('<div class="trade-unit">' + msg.trades_data[i][3] + '<div>');
      $newTrade.append('<div class="trade-unit">' + msg.trades_data[i][4] + '<div>');
      $('.trade-history-list').append($newTrade);
    }
    let datetime_arr = new Array();
    for (let i = 0; i < msg.candlesticks_datetime.length; i++) {
      var datetime_value = new Date(msg.candlesticks_datetime[i]).toLocaleTimeString('en-GB');
      datetime_arr.push(datetime_value);
    }
    trade_chart.data.labels = datetime_arr;
    trade_chart.data.datasets[0].data = msg.candlesticks_data;
    trade_chart.update();
  });

  $(".line").click(function(){
    if (this.id != room) {
        $('#' + room).removeClass("active");
        leaveRoom(room);
        joinRoom(this.id);
        room = this.id;
        $(this).addClass("active");
        trade_chart.data.labels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1];
        trade_chart.data.datasets[0].data = [];
        trade_chart.update();
        $.ajax({
          type: 'POST',
          url: '/get_bot_data',
          data: {'bot_id': room},
          success: function(request) {
            $('.bot-strategy-name').text(request.strategy_name);
            $('.bot-strategy-description').css("border-top", "1px solid gray");
            $('.bots-delete').show();
            $('.bot-strategy-description').text(request.strategy_description);
            $('.trade-history-list').empty();
            for (let i = 0; i < request.bot_trades.length; i++) {
              var $newTrade = $('<div/>').addClass('trade-line');
              if (i == request.bot_trades.length - 1) {
                $newTrade.css("border-bottom", "0");
              }
              $newTrade.append('<div class="trade-unit">' + request.bot_trades[i][0] + '<div>');
              $newTrade.append('<div class="trade-unit">' + request.bot_trades[i][1] + '<div>');
              $newTrade.append('<div class="trade-unit">' + request.bot_trades[i][2] + '<div>');
              $newTrade.append('<div class="trade-unit">' + request.bot_trades[i][3] + '<div>');
              $newTrade.append('<div class="trade-unit">' + request.bot_trades[i][4] + '<div>');
              $('.trade-history-list').append($newTrade);
            }
          }
        });
    }
  });

  function leaveRoom(room) {
    socket.emit('leave', {'room': room});
  };

  function joinRoom(room) {
    socket.emit('join', {'room': room});
  };

  $(".bots-delete").click(function() {
    $.ajax({
    type: 'POST',
    url: '/delete_bot',
    data: {'bot_id': room},
    success: function(request) {
      if (request.bot_id != 'None') {
        $('#' + request.bot_id).remove();
        room = 'None';
        $('.bot-strategy-name').empty();
        $('.bots-delete').hide();
        $('.bot-strategy-description').css("border-top", "0");
        $('.bot-strategy-description').empty();
      }
      }
    });
  });

  $(".start_bot").click(function() {
    $.ajax({
    type: 'POST',
    url: '/start_bot',
    data: {'bot_id': room},
    success: function(request) {
      if (request.bot_id != 'None') {
        $('#' + request.bot_id).children().eq(5).text('active');
      }
      }
    });
  });

  $(".soft_stop").click(function() {
    $.ajax({
    type: 'POST',
    url: '/soft_stop_bot',
    data: {'bot_id': room},
    success: function(request) {
      if (request.bot_id != 'None') {
        $('#' + request.bot_id).children().eq(5).text('waiting');
      }
      }
    });
  });

  $(".hard_stop").click(function() {
    $.ajax({
    type: 'POST',
    url: '/hard_stop_bot',
    data: {'bot_id': room},
    success: function(request) {
      if (request.bot_id != 'None') {
        $('#' + request.bot_id).children().eq(5).text('stop');
      }
      }
    });
  });

  $('.start_bot').hover(
    function() {
      $('.bot-buttons-description').css('background', 'rgb(80, 216, 90)');
      $('.bot-buttons-description').html(
      'Запускает бота если он ещё не запущен. <br> Бот будет работать до тех пор, пока вы его не остановите.');
      $('.bot-buttons-description').fadeIn();
    },
    function() {
      $('.bot-buttons-description').hide();
    }
  );

  $('.soft_stop').hover(
    function() {
      $('.bot-buttons-description').css('background', 'rgb(238, 238, 18)');
      $('.bot-buttons-description').html(
      'Переводит бота в режим ожидания. <br> Бот будет работать до тех пор, пока не закроет текущую сделку.');
      $('.bot-buttons-description').fadeIn();
    },
    function() {
      $('.bot-buttons-description').hide();
    }
  );

  $('.hard_stop').hover(
    function() {
      $('.bot-buttons-description').css('background', 'rgb(240, 61, 61)');
      $('.bot-buttons-description').html(
      'Принудительно останавливает работу бота. <br> Бот закрывает текущую сделку немедленно, если она есть.');
      $('.bot-buttons-description').fadeIn();
    },
    function() {
      $('.bot-buttons-description').hide();
    }
  );

  const labels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1];

  const data = {
    labels: labels,
    datasets: [{
      label: 'TRADING PAIR',
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      data: [],
    }]
  };

  const config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
        animation: {
          duration: 0,
      },
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