function get_forecast(match_id) {
$.ajax({
    type: "POST",
    url: "/get_forecast",
    data: {match_id: match_id, home_goal: $('#home_goal' + match_id).val(), guest_goal: $('#guest_goal' + match_id).val()},
    success: function(response) {
        alert('successfully submitted');
       
    }
});
}
