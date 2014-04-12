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
	status = data['comms-status'];
	if (status == '1') {
		updateCommsStatus("COMMS_UP");
	} else {
		updateCommsStatus("COMMS_DOWN");
	}
	updateGameClock(data['game-time']);
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