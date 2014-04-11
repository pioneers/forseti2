function populateGameClock() {
	$.get('/api/v1/game-time', {}, function(data) {
		$('#game-clock').text(data);
	});
	$.get('/api/v1/comms-status', {}, function(data) {
		$('#comms-status').text(data);
	});
}

function main_loop() {
	d = new Date();
	time = d.toLocaleTimeString();
	$('#wall-clock').text(time);
	populateGameClock();
}

$( document ).ready(function() {
	window.setInterval(main_loop, 100);
});