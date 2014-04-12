function updateCommsStatus(status) {
	status_span = $('#config-status');
	status_span.removeClass("label-info");
	status_span.removeClass("label-warning");
	status_span.removeClass("label-danger");
	status_span.removeClass("label-success");
	switch(status) {
		case "COMMS_UP":
			status_span.addClass("label-success");
			status_span.text("Connected to Server");
			break;
		case "COMMS_DOWN":
			status_span.addClass("label-warning");
			status_span.text("LCM Pings Offline...")
			break;
		case "INFO_FAILED":
			status_span.addClass("label-danger");
			status_span.text("Can't Connect to Flask Server...")
			break;
	}
}

function updateGameClock(gametime, mode) {
	// convert input "gametime" into 
	if (gametime > 140) {
		time = 0;
	} else if (gametime > 20) {
		time = 140 - gametime;
	} else {
		time = 20 - gametime;
	}

	minutes = Math.floor(time / 60);
	seconds = Math.floor(time % 60);
	microseconds = Math.floor(time % 1);

	if (seconds < 10) {
		hr_seconds = "0" + String(seconds);
	} else {
		hr_seconds = String(seconds);
	}
	hr_time = String(minutes) + ":" + hr_seconds;
	game_clock = $('#game-clock');
	game_clock.text(hr_time);

	clock_bar = $('#clock-bar');
	clock_bar.removeClass("progress-bar-info");
	clock_bar.removeClass("progress-bar-warning");
	clock_bar.removeClass("progress-bar-danger");
	if (time > 30) {
	} else if (time <= 10) {
		clock_bar.addClass("progress-bar-danger");
	} else if (time <= 30) {
		clock_bar.addClass("progress-bar-warning");
	}

	game_mode_div = $('#game-mode');
	switch (mode) {
		case "Setup":
			clock_bar.css("width", "100%");
			game_mode_div.text("Setup");
			break;
		case "Teleop":
			clock_bar.css("width", String(time / 120 * 100) + "%");
			game_mode_div.text("Teleoperated Mode");
			break;
		case "Autonomous":
			game_mode_div.text("Autonomous Mode");
			clock_bar.css("width", String(time / 20 * 100) + "%");
			break;
		case "Paused":
			game_mode_div.text("Match Paused");
			clock_bar.css("width", "0%");
			break;
		case "End":
			game_mode_div.text("Match Ended");
			break;
		default:
			game_mode_div.text("Unknown Mode");
			break;
	}
}

function updateScore(data) {
	blue_scores = data['blue_points'];
	gold_scores = data['gold_points'];
	$('#blue-total-score').text(blue_scores[0]);
	$('#gold-total-score').text(gold_scores[0]);
	$('#blue-normal-points').text(blue_scores[1]);
	$('#gold-normal-points').text(gold_scores[1]);
	$('#blue-permanent-points').text(blue_scores[2]);
	$('#gold-permanent-points').text(gold_scores[2]);
	$('#blue-penalties').text(-blue_scores[3]);
	$('#gold-penalties').text(-gold_scores[3]);

}

function processInfo(data) {
	status = data['comms-status'];
	if (status == '1') {
		updateCommsStatus("COMMS_UP");
	} else {
		updateCommsStatus("COMMS_DOWN");
	}
	updateGameClock(data['game-time'], data['game-mode']);
	$('#heartbeat').text(data['stored-a']);

	updateScore(data);
}

function failedToGetInfo() {
	updateCommsStatus("INFO_FAILED");
}
		
function updateInterface() {
	// set wall clock
	time = new Date().toLocaleTimeString();
	$('#wall-clock').text(time);

	$.get('/api/v1/all-info', {}, processInfo).fail(failedToGetInfo);
}

$( document ).ready(function() {
	window.setInterval(updateInterface, 100);
});