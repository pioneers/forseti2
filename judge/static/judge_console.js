function processInfo(data) {
	$('#game-clock').text(data['game-clock']);
	$('#comms-status').text(data['comms-status']);
}

function updateInterface() {
	// set wall clock
	time = new Date().toLocaleTimeString();
	$('#wall-clock').text(time);

	$.get('/api/v1/all-info', {}, processInfo);
}

$( document ).ready(function() {
	window.setInterval(updateInterface, 100);
});