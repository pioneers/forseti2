function updateInterface() {
  // set wall clock
  time = new Date().toLocaleTimeString();
  $('#wall-clock').text(time);
}

function submitAdjustment() {
  $.post('/api/v1/score-delta', $(this).serialize());
  $('#adjust-form')[0].reset();
}

$( document ).ready(function() {
  window.setInterval(updateInterface, 100);
  $('form').submit(submitAdjustment);
});
