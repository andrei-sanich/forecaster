from flask_wtf import FlaskForm
from wtforms import IntegerField,SelectField, StringField, TextAreaField, BooleanField,\
    SubmitField, DateTimeField 
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import Role, User, Match, League, Team


class LeagueForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(0, 64)])
    season = StringField('Сезон', validators=[
        DataRequired(),
        Regexp('^\d\d\/\d\d$', 0,
        'Сезон в в формате yy/yy'
        )])
    submit = SubmitField('Отправить')

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class MatchForm(FlaskForm):
    league = SelectField('Лига', coerce=int, validators=[DataRequired()])
    home_team = SelectField('Домашняя команда', coerce=int, validators=[DataRequired()])
    guest_team = SelectField('Гостевая команда', coerce=int, validators=[DataRequired()])
    timestamp = DateTimeField('Дата', format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Отправить')

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        self.league.choices = [
            (row.league_id, row.name) for row in League.query.order_by(League.name).all()]
        league = League.query.order_by(League.name).first()
        self.home_team.choices = [
            (row.team_id, row.name) for row in Team.query.join(
                Team.leagues).filter_by(league_id=league.league_id).all()]
        self.guest_team.choices = [
            (row.team_id, row.name) for row in Team.query.join(
                Team.leagues).filter_by(league_id=league.league_id).all()]
