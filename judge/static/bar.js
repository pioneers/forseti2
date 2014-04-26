$( document ).ready(function($) {
	$('#heartbeat').tooltip({title: "Press the guide button", placement: 'bottom'});
	$('form').submit(submitAdjustment);
	$('input.diff').on('input', recalculateTotals);
	$('input.new').on('input', recalculateDiffs);
});