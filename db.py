
import datetime

from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types import ChoiceType

from config import app

db = SQLAlchemy(app)


class Note(db.Model):
    classifier_choices = [
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('important', 'Important'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    classifier = db.Column(ChoiceType(classifier_choices))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Note %r %r>' % (self.created_date, self.text)

    @staticmethod
    def create_note(text, classifier):
        note = Note(text=text, classifier=classifier)
        db.session.add(note)
        db.session.commit()

    @staticmethod
    def list_notes(days=3):
        return Note.query.filter(Note.created_date > datetime.datetime.now() - datetime.timedelta(days=days))


class Auth(object):

    @staticmethod
    def save(access_token, refresh_token, expiry):
        # Session is totally a DB ;)
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session['expiry_date'] = expiry

    @staticmethod
    def get_access_token():
        return session.get('access_token')

    @staticmethod
    def get_refresh_token():
        return session.get('refresh_token')

    @staticmethod
    def is_auth_expired():
        expiry_timestamp = session.get('expiry')
        return datetime.datetime.fromtimestamp(int(expiry_timestamp)) < datetime.datetime.now()
