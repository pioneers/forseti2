function updateCommsStatus(status) {
	heading = $('#config-heading');
	heading.removeClass("btn-info");
	heading.removeClass("btn-warning");
	heading.removeClass("btn-danger");
	heading.removeClass("btn-success");
	status_span = $('#config-status');
	status_span.removeClass("label-info");
	status_span.removeClass("label-warning");
	status_span.removeClass("label-danger");
	status_span.removeClass("label-success");
	switch(status) {
		case "COMMS_UP":
			heading.addClass("btn-success")
			status_span.addClass("label-success");
			status_span.text("Connected to Server");
			break;
		case "COMMS_DOWN":
			heading.addClass("btn-warning")
			status_span.addClass("label-warning");
			status_span.text("LCM Communications Offline...")
			break;
		case "INFO_FAILED":
			heading.addClass("btn-danger")
			status_span.addClass("label-danger");
			status_span.text("Can't Connect to Flask Server...")
			break;
		default:
			heading.addClass("btn-danger")
			status_span.addClass("label-danger");
			status_span.text("Unknown Error")
	}
}

function updateGameClock(data) {
	mode = data['stage_name'];
	stage_time = data['stage_time'];
	total_stage_time = data['total_stage_time'];
	// convert input "gametime" into 
	time = total_stage_time - stage_time;

	minutes = Math.floor(time / 60);
	seconds = Math.floor(time % 60);
	disp_seconds = Math.ceil(time % 60);

	if (disp_seconds < 10) {
		hr_seconds = "0" + String(disp_seconds);
	} else {
		hr_seconds = String(disp_seconds);
	}
	hr_time = String(minutes) + ":" + hr_seconds;
	game_clock = $('#game-clock');
	game_clock.text(hr_time);

	clock_bar = $('#clock-bar');
	clock_bar.css("width", String(time / total_stage_time * 100) + "%");
	clock_bar.removeClass("progress-bar-info");
	clock_bar.removeClass("progress-bar-warning");
	clock_bar.removeClass("progress-bar-danger");
	if (time > 30) {
	} else if (time <= 10) {
		clock_bar.addClass("progress-bar-danger");
	} else if (time <= 30) {
		clock_bar.addClass("progress-bar-warning");
	}

	bonus_bar = $('#bonus-bar');
	bonus_time = data['bonus_time']
	bonus_bar.css("width", String(bonus_time / 30 * 100) + "%");

	game_mode_div = $('#game-mode');
	switch (mode) {
		case "Setup":
			game_mode_div.text("Setup");
			clock_bar.css("width", "100%");
			break;
		case "Teleop":
			game_mode_div.text("Teleoperated Mode");
			break;
		case "Autonomous":
			game_mode_div.text("Autonomous Mode");
			break;
		case "Paused":
			game_mode_div.text("Match Paused");
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
	// update the team names
	team_numbers = data['team_numbers'];
	team_names = data['team_names'];
	var team_strings = new Array();
	for (var i = 0; i < 4; i++) {
		team_strings[i] = String(team_numbers[i]) + " " + team_names[i];
		$('#team' + String(i)).text(team_strings[i]);
	}
	// update match number
	match_number = data['match_number'];
	$('#match-number').text(match_number)


	// update the scores
	blue_scores = data['blue_points'];
	gold_scores = data['gold_points'];
	$('#blue-total-score').text(blue_scores[0]);
	$('#gold-total-score').text(gold_scores[0]);
	$('#blue-autonomous-points').text(blue_scores[1]);
	$('#gold-autonomous-points').text(gold_scores[1]);
	$('#blue-normal-points').text(blue_scores[2]);
	$('#gold-normal-points').text(gold_scores[2]);
	$('#blue-permanent-points').text(blue_scores[3]);
	$('#gold-permanent-points').text(gold_scores[3]);
	$('#blue-penalties').text(-blue_scores[4]);
	$('#gold-penalties').text(-gold_scores[4]);

  if (data['bonus_possession'] == 2) {
	$('#blue-bonus-points').text(data['bonus_points'])
	$('#gold-bonus-points').text("");
  } else if (data['bonus_possession'] == 1) {
	$('#blue-bonus-points').text("");
	$('#gold-bonus-points').text(data['bonus_points'])
  } else {
	$('#blue-bonus-points').text("");
	$('#gold-bonus-points').text("");
  }

	$('#old_blue_total_score').text(blue_scores[0]);
	$('#old_gold_total_score').text(gold_scores[0]);
	$('#old_blue_autonomous_points').text(blue_scores[1]);
	$('#old_gold_autonomous_points').text(gold_scores[1]);
	$('#old_blue_normal_points').text(blue_scores[2]);
	$('#old_gold_normal_points').text(gold_scores[2]);
	$('#old_blue_permanent_points').text(blue_scores[3]);
	$('#old_gold_permanent_points').text(gold_scores[3]);
	$('#old_blue_penalty').text(blue_scores[4]);
	$('#old_gold_penalty').text(gold_scores[4]);
	$('#old_bonus_points').text(data['bonus_points']);
	recalculateTotals();
}

function updateHeartbeat(data) {
	hb = $('#heartbeat');
	if (data['stored_a']) {
		hb.addClass('btn-info');
	} else {
		hb.removeClass('btn-info');
	}
}

function processInfo(data) {
	updateCommsStatus(data['comms_status']);
	updateGameClock(data);
	updateScore(data);
	updateHeartbeat(data);
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

function submitAdjustment(e) {
	e.preventDefault();
	$.post('/api/v1/score-delta', $(this).serialize());
	recalculateTotals();
	$('#adjust-form')[0].reset();
}

function totalHelper(name) {
  $("#new_" + name).val(parseInt($("#old_" + name).text()) + parseInt($("input[name=" + name + "]").val()));
}

function diffHelper(name) {
  $("input[name=" + name + "]").val(parseInt($("#new_" + name).val()) - parseInt($("#old_" + name).text()));
}

function recalculateTotals() {
  totalHelper("blue_autonomous_points");
  totalHelper("gold_autonomous_points");
  totalHelper("blue_normal_points");
  totalHelper("gold_normal_points");
  totalHelper("blue_permanent_points");
  totalHelper("gold_permanent_points");
  totalHelper("blue_penalty");
  totalHelper("gold_penalty");
  totalHelper("bonus_points");

  recalculateSum();
}

function recalculateDiffs() {
  diffHelper("blue_autonomous_points");
  diffHelper("gold_autonomous_points");
  diffHelper("blue_normal_points");
  diffHelper("gold_normal_points");
  diffHelper("blue_permanent_points");
  diffHelper("gold_permanent_points");
  diffHelper("blue_penalty");
  diffHelper("gold_penalty");
  diffHelper("bonus_points");

  recalculateSum();
}

function recalculateSum() {
  $("#new_blue_total_score").text(
	parseInt($("#new_blue_autonomous_points").val()) +
	  parseInt($("#new_blue_normal_points").val()) +
	  parseInt($("#new_blue_permanent_points").val()) +
      (parseInt($("#blue-bonus-points").text()) || 0) -
	  parseInt($("#new_blue_penalty").val())
  );
  $("#diff_blue_total_score").text(
	parseInt($("#new_blue_total_score").text()) -
	  parseInt($("#old_blue_total_score").text()));
  $("#new_gold_total_score").text(
	parseInt($("#new_gold_autonomous_points").val()) +
	  parseInt($("#new_gold_normal_points").val()) +
	  parseInt($("#new_gold_permanent_points").val()) +
      (parseInt($("#gold-bonus-points").text()) || 0) -
	  parseInt($("#new_gold_penalty").val())
  );
  $("#diff_gold_total_score").text(
	parseInt($("#new_gold_total_score").text()) -
	  parseInt($("#old_gold_total_score").text()));
}

$( document ).ready(function($) {
	window.setInterval(updateInterface, 40);
	$('#heartbeat').tooltip({title: "Press the guide button", placement: 'bottom'});
	$('form').submit(submitAdjustment);
	$('input.diff').on('input', recalculateTotals);
	$('input.new').on('input', recalculateDiffs);
});