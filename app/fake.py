from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Match, Team, League


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def teams(count=100):
    fake = Faker()
    i = 0
    while i < count:
        team = Team(
            name=fake.name())
        db.session.add(team)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()



def leagues(count=5):
    fake = Faker()
    i = 0
    while i < count:
        league = League(
            name=fake.name())
        db.session.add(league)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()           


def team_league(count=1000):
    i = 0
    team_count = Team.query.count()
    league_count = League.query.count()
    while i < count:
        t = Team.query.offset(randint(0, team_count - 1)).first()
        l = League.query.offset(randint(0, league_count - 1)).first()
        t.leagues.append(l)
        db.session.add(t)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()


def matches(count=40):
    i = 0
    fake = Faker()
    league_count = League.query.count()
    while i < count:
        l = League.query.offset(randint(0, league_count - 1)).first()
        team_count = l.teams.count()
        guest_team = l.teams.offset(randint(0, team_count - 1)).first()
        home_team = l.teams.offset(randint(0, team_count - 1)).first()
        m = Match(
            guest_team=guest_team.name,
            home_team=home_team.name,
            league=l.name,
            timestamp=fake.past_date())
        db.session.add(m)
        try:
            db.session.commit()
            i += 1
        except:
            db.session.rollback()            
