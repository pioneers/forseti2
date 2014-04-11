function updateGameClock(time) {
	minutes = Math.floor(time / 60);
	seconds = Math.floor(time % 60);
	microseconds = Math.floor(time % 1);

	if (seconds < 10) {
		hr_seconds = "0" + String(seconds);
	} else {
		hr_seconds = String(seconds);
	}
	hr_time = String(minutes) + ":" + hr_seconds;
	$('#game-clock').text(hr_time);

	proportionRemaining = time / 120;
	clock_bar = $('#clock-bar');
	clock_bar.css("width", String(proportionRemaining * 100) + "%");

	clock_bar.removeClass("progress-bar-info");
	clock_bar.removeClass("progress-bar-warning");
	clock_bar.removeClass("progress-bar-danger");
	if (time >= 30) {
		clock_bar.addClass("progress-bar-info");
	} else if (time < 30) {
		clock_bar.addClass("progress-bar-warning");
	} else if (time < 10) {
		clock_bar.addClass("progress-bar-danger");
	}
}

function processInfo(data) {
	updateGameClock(data['game-time']);
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