$(document).ready(function() {
  $('.flash-close').click(function() {
    $(this).parent().parent().remove();
  });
});