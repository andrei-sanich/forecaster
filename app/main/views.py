from flask import render_template, redirect, url_for, abort, flash, request, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, MatchForm, LeagueForm
from .. import db
from ..models import Role, User, Match, Permission, League, Team, Forecast
from ..decorators import admin_required, moderate_required


@main.route('/', methods=['GET', 'POST'])
def index():

    matches = Match.query.order_by(Match.timestamp.asc()).all()
    return render_template('index.html', matches=matches)


@main.route('/rating')
def rating():

    ratings = db.session.query(
        User.username,
        User.points,
        db.func.count(Forecast.user_id).label('counter')
        ).join(
            Forecast,
            User.id == Forecast.user_id
            ).group_by(
                User.username,
                User.points
                ).order_by(User.points.desc()).all()
    return render_template('rating.html', ratings=ratings)


@main.route('/team/<int:league>')
def team(league):

    teams = Team.query.join(Team.leagues).filter_by(league_id=league).all()
    teamArray = []
    for team in teams:
        teamObj = {}
        teamObj['team_id'] = team.team_id
        teamObj['name'] = team.name
        teamArray.append(teamObj)
    return jsonify({'teams': teamArray})


@main.route('/user/<username>')
def user(username):

    username = User.query.filter_by(username=username).first_or_404()
    matches = db.session.query(
        Match,
        Forecast).filter(
            Forecast.match_id == Match.id,
            Forecast.user_id == current_user.id).all()
    return render_template('user.html', user=username, matches=matches)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):

    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/get_forecast', methods=['GET', 'POST'])
@login_required
def get_forecast():

    input_forecast = request.form.to_dict()
    match_id = int(input_forecast['match_id'])
    forecast_user = Forecast.query.filter_by(
        match_id=match_id, user_id=current_user.id).first()
    if forecast_user is None:
        forecast = Forecast(
            home_goal=int(input_forecast['home_goal']),
            guest_goal=int(input_forecast['guest_goal']),
            user_id=current_user.id,
            match_id=match_id)
        db.session.add(forecast)
        db.session.commit()
    forecast_user.home_goal = int(input_forecast['home_goal'])
    forecast_user.guest_goal = int(input_forecast['guest_goal'])
    db.session.add(forecast_user)
    db.session.commit()
    return redirect(url_for('.index'))


@main.route('/add_league', methods=['GET', 'POST'])
@login_required
@moderate_required
def add_league():

    league_form = LeagueForm()
    if league_form.validate_on_submit():
        new_league = League(
            league_form.name.data,
            league_form.season.data)
        db.session.add(new_league)
        db.session.commit()
    return render_template('add_league.html', league_form=league_form)


@main.route('/add_match', methods=['GET', 'POST'])
@login_required
@moderate_required
def add_match():

    match_form = MatchForm()
    global team_choices
    if request.method == 'POST':
        if request.content_type == 'application/json':
            teams = request.get_json()['teams']
            team_choices = [(team['team_id'], team['name']) for team in teams]
            match_form.home_team.choices = team_choices
            match_form.guest_team.choices = team_choices
        else:
            match_form.home_team.choices = team_choices
            match_form.guest_team.choices = team_choices
            league = dict(
                match_form.league.choices).get(int(match_form.league.data), "Not")
            home_team = dict(
                match_form.home_team.choices).get(int(match_form.home_team.data), "Not")
            guest_team = dict(
                match_form.guest_team.choices).get(int(match_form.guest_team.data), "Not")
            if match_form.validate_on_submit():
                match = Match(
                    home_team=home_team,
                    guest_team=guest_team,
                    league=league,
                    timestamp=match_form.timestamp.data)
                db.session.add(match)
                db.session.commit()
                return redirect(url_for('.add_match'))
    return render_template('add_match.html', match_form=match_form)


@main.route('/statistic', methods=['GET'])
@login_required
@moderate_required
def statistic():

    return render_template('statistic.html')


@main.route('/counting_results', methods=['GET'])
@login_required
@moderate_required
def counting_results():

    matches = Match.query.filter_by(is_actual=True).all()
    for match in matches:
        if match.home_goal and match.guest_goal is not None:
            forecasts = match.forecasts
            fact_goals = (match.home_goal, match.guest_goal)
            for forecast in forecasts:
                user = User.query.filter_by(
                    id=forecast.user_id).first() 
                forecast_goals = (forecast.home_goal, forecast.guest_goal)
                points = _get_points(
                    fact_hg=fact_goals[0],
                    fact_gg=fact_goals[1],
                    forecast_hg=forecast_goals[0],
                    forecast_gg=forecast_goals[1])
                if points > 0:
                    user.points += points
                    db.session.add(user)
                    db.session.commit()
            match.is_actual = False
            db.session.add(match)
            db.session.commit()


def _get_points(fact_hg, fact_gg, forecast_hg, forecast_gg):

    if fact_hg == forecast_hg and fact_gg == forecast_gg:
        points = 5
        return points
    elif (fact_hg - fact_gg) == (forecast_hg - forecast_gg):
        points = 3
        return points
    elif fact_hg - fact_gg > 0 and forecast_hg - forecast_gg > 0:
        points = 1
        return points
    elif fact_hg - fact_gg < 0 and forecast_hg - forecast_gg < 0:
        points = 1
        return points
    else:
        points = 0
        return points
