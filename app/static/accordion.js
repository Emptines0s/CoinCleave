var accordion = function() {
  var data = $(".accordion-head").on("click", function() {
    if (!$(this).hasClass("active") && !$(this).hasClass("waiting")) {
      $(this).toggleClass("waiting");
    }
    $(this).next(".accordion-body").not(".animated").slideToggle("fast", function() {
      if ($(this).prev().hasClass("active")) {
        $(this).prev().toggleClass("active");
      }
      if ($(this).prev().hasClass("waiting")) {
        $(this).prev().toggleClass("waiting");
        $(this).prev().toggleClass("active");
      }
    });
  })
}

var scroll = function() {
  $('html, body').animate({scrollTop: $("#" + target).offset().top}, 500).promise().done(function() {
    $("#" + target + ".accordion-head").addClass("waiting");
    $("#" + target + ".accordion-head").next(".accordion-body").not(".animated").slideToggle("fast", function() {
      $(this).prev().removeClass("waiting");
      $(this).prev().addClass("active");
    });
  });
}

accordion();
scroll();