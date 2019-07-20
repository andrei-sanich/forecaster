let league_select = document.getElementById('league');
let hometeam_select = document.getElementById('home_team');
let guestteam_select = document.getElementById('guest_team');

league_select.onchange = function() {
    league = league_select.value;

    fetch('/team/' + league, { credentials: 'include' }).then(function(response) {

        response.json().then(function(data) {
            let optionHTML = '';
            
            for (let team of data.teams) {
                optionHTML += "<option value='" + team.team_id + "'>" + team.name + "</option>";
            }
            hometeam_select.innerHTML = optionHTML;
            guestteam_select.innerHTML = optionHTML;

            fetch('/moderate', {
              credentials: 'include',
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(data)
            })
            });


    });
}
    